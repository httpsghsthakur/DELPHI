import torch
import torch.nn as nn
import torch.nn.functional as F
from .config import CausalSeqConfig
from typing import Tuple, Dict

class EncoderLSTM(nn.Module):
    def __init__(self, config: CausalSeqConfig):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=config.input_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.encoder_layers,
            dropout=config.dropout if config.encoder_layers > 1 else 0.0,
            bidirectional=config.bidirectional_encoder,
            batch_first=True
        )
        self.bidirectional = config.bidirectional_encoder
        self.hidden_dim = config.hidden_dim
        
        # If bidirectional, we need to map the hidden states back to hidden_dim for decoder
        if self.bidirectional:
            self.hidden_map = nn.Linear(config.hidden_dim * 2, config.hidden_dim)
            self.cell_map = nn.Linear(config.hidden_dim * 2, config.hidden_dim)
            
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        x: (batch_size, seq_len, input_dim)
        mask: (batch_size, seq_len) boolean mask where True = valid, False = pad
        """
        # Pack sequence if mask is provided
        if mask is not None:
            lengths = mask.sum(dim=1).cpu()
            # Enforce lengths > 0 for packing
            lengths = torch.clamp(lengths, min=1)
            packed_x = nn.utils.rnn.pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
            packed_outputs, (hidden, cell) = self.lstm(packed_x)
            outputs, _ = nn.utils.rnn.pad_packed_sequence(packed_outputs, batch_first=True, total_length=x.size(1))
        else:
            outputs, (hidden, cell) = self.lstm(x)
            
        if self.bidirectional:
            # outputs: (batch, seq, 2*hidden)
            # hidden: (2*num_layers, batch, hidden) -> needs to become (num_layers, batch, hidden)
            # We concatenate forward and backward states for the last layer
            hidden = self._combine_bidir_states(hidden)
            cell = self._combine_bidir_states(cell)
            
        return outputs, (hidden, cell)

    def _combine_bidir_states(self, state: torch.Tensor) -> torch.Tensor:
        # state is (num_layers * num_directions, batch, hidden_size)
        num_layers = state.size(0) // 2
        batch_size = state.size(1)
        hidden_size = state.size(2)
        
        state = state.view(num_layers, 2, batch_size, hidden_size)
        forward_state = state[:, 0, :, :]
        backward_state = state[:, 1, :, :]
        combined = torch.cat([forward_state, backward_state], dim=-1)
        
        # map to hidden_dim
        mapped = self.hidden_map(combined) if hasattr(self, 'hidden_map') else combined
        return mapped


class BahdanauAttention(nn.Module):
    def __init__(self, hidden_dim: int, encoder_dim: int):
        super().__init__()
        self.Wa = nn.Linear(hidden_dim, hidden_dim)
        self.Ua = nn.Linear(encoder_dim, hidden_dim)
        self.Va = nn.Linear(hidden_dim, 1)

    def forward(self, decoder_hidden: torch.Tensor, encoder_outputs: torch.Tensor, mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        decoder_hidden: (batch_size, hidden_dim)  -- top layer hidden state
        encoder_outputs: (batch_size, seq_len, encoder_dim)
        mask: (batch_size, seq_len) True=valid
        """
        # score = Va(tanh(Wa(s) + Ua(h)))
        # decoder_hidden: (batch, hidden) -> (batch, 1, hidden)
        query = self.Wa(decoder_hidden).unsqueeze(1)
        keys = self.Ua(encoder_outputs)
        
        scores = self.Va(torch.tanh(query + keys)).squeeze(2) # (batch, seq_len)
        
        if mask is not None:
            # Mask out padding with a large negative number before softmax
            scores = scores.masked_fill(~mask, -1e9)
            
        attention_weights = F.softmax(scores, dim=-1) # (batch, seq_len)
        
        # context: (batch, 1, seq_len) @ (batch, seq_len, encoder_dim) -> (batch, 1, encoder_dim)
        context = torch.bmm(attention_weights.unsqueeze(1), encoder_outputs)
        
        return context.squeeze(1), attention_weights


class DecoderLSTM(nn.Module):
    def __init__(self, config: CausalSeqConfig):
        super().__init__()
        self.hidden_dim = config.hidden_dim
        encoder_out_dim = config.hidden_dim * 2 if config.bidirectional_encoder else config.hidden_dim
        
        # The input to the decoder at each step is the previous generated event representation (e.g., event_type embedding)
        # For simplicity in this architecture, we use an embedded representation of the previous prediction.
        # Since we have multiple heads, we embed the event_type and time_bin as primary drivers.
        self.event_embed = nn.Embedding(config.num_event_types + 3, config.hidden_dim // 2) # +3 for BOS/EOS/PAD
        self.time_embed = nn.Embedding(config.num_time_bins + 3, config.hidden_dim // 2)
        
        self.attention = BahdanauAttention(config.hidden_dim, encoder_out_dim)
        
        # LSTM input: context_vector + embedded_previous_step
        self.lstm = nn.LSTM(
            input_size=encoder_out_dim + config.hidden_dim,
            hidden_size=config.hidden_dim,
            num_layers=config.decoder_layers,
            dropout=config.dropout if config.decoder_layers > 1 else 0.0,
            batch_first=True
        )
        
        # Output heads
        self.event_type_head = nn.Linear(config.hidden_dim, config.num_event_types + 3)
        self.time_head = nn.Linear(config.hidden_dim, config.num_time_bins + 3)
        self.actor_head = nn.Linear(config.hidden_dim, config.num_actors)
        self.target_head = nn.Linear(config.hidden_dim, config.num_targets)
        self.domain_head = nn.Linear(config.hidden_dim, config.num_domains)
        
    def forward(
        self, 
        prev_event_type: torch.Tensor, 
        prev_time_bin: torch.Tensor,
        hidden: Tuple[torch.Tensor, torch.Tensor],
        encoder_outputs: torch.Tensor,
        mask: torch.Tensor = None
    ):
        # prev_event_type: (batch)
        # prev_time_bin: (batch)
        emb_evt = self.event_embed(prev_event_type) # (batch, hidden/2)
        emb_time = self.time_embed(prev_time_bin) # (batch, hidden/2)
        step_input = torch.cat([emb_evt, emb_time], dim=-1) # (batch, hidden)
        
        # Extract top layer hidden state for attention
        # hidden[0] is (num_layers, batch, hidden)
        top_hidden = hidden[0][-1] 
        
        context, attn_weights = self.attention(top_hidden, encoder_outputs, mask) # context: (batch, enc_out_dim)
        
        lstm_input = torch.cat([step_input, context], dim=-1).unsqueeze(1) # (batch, 1, enc_out_dim + hidden)
        
        output, new_hidden = self.lstm(lstm_input, hidden)
        output = output.squeeze(1) # (batch, hidden)
        
        # Generate predictions
        pred_event_type = self.event_type_head(output)
        pred_time = self.time_head(output)
        pred_actor = self.actor_head(output)
        pred_target = self.target_head(output)
        pred_domain = self.domain_head(output)
        
        preds = {
            "event_type": pred_event_type,
            "time_bin": pred_time,
            "actor": pred_actor,
            "target": pred_target,
            "domain": pred_domain
        }
        
        return preds, new_hidden, attn_weights


class CausalSeq(nn.Module):
    def __init__(self, config: CausalSeqConfig):
        super().__init__()
        self.config = config
        self.encoder = EncoderLSTM(config)
        self.decoder = DecoderLSTM(config)
        
        # BOS/EOS/PAD tokens (assuming they are placed at the end of the vocab)
        self.PAD_IDX = config.num_event_types
        self.BOS_IDX = config.num_event_types + 1
        self.EOS_IDX = config.num_event_types + 2
        
        self.TIME_PAD_IDX = config.num_time_bins
        self.TIME_BOS_IDX = config.num_time_bins + 1
        self.TIME_EOS_IDX = config.num_time_bins + 2
        
    def forward(self, src: torch.Tensor, src_mask: torch.Tensor, tgt_event_type: torch.Tensor, tgt_time_bin: torch.Tensor, teacher_forcing_ratio: float = 0.5):
        """
        src: (batch, seq_len, 256)
        src_mask: (batch, seq_len)
        tgt_event_type: (batch, tgt_len) - including BOS
        tgt_time_bin: (batch, tgt_len) - including BOS
        """
        batch_size = src.size(0)
        tgt_len = tgt_event_type.size(1)
        
        encoder_outputs, hidden = self.encoder(src, src_mask)
        
        # Tensors to store predictions
        outputs_event = torch.zeros(batch_size, tgt_len, self.config.num_event_types + 3).to(src.device)
        outputs_time = torch.zeros(batch_size, tgt_len, self.config.num_time_bins + 3).to(src.device)
        outputs_actor = torch.zeros(batch_size, tgt_len, self.config.num_actors).to(src.device)
        outputs_target = torch.zeros(batch_size, tgt_len, self.config.num_targets).to(src.device)
        outputs_domain = torch.zeros(batch_size, tgt_len, self.config.num_domains).to(src.device)
        
        # Initial input to decoder is BOS
        prev_evt = tgt_event_type[:, 0]
        prev_time = tgt_time_bin[:, 0]
        
        # We start from step 1 (step 0 is BOS)
        for t in range(1, tgt_len):
            preds, hidden, _ = self.decoder(prev_evt, prev_time, hidden, encoder_outputs, src_mask)
            
            outputs_event[:, t] = preds["event_type"]
            outputs_time[:, t] = preds["time_bin"]
            outputs_actor[:, t] = preds["actor"]
            outputs_target[:, t] = preds["target"]
            outputs_domain[:, t] = preds["domain"]
            
            teacher_force = torch.rand(1).item() < teacher_forcing_ratio
            top1_evt = preds["event_type"].argmax(1)
            top1_time = preds["time_bin"].argmax(1)
            
            prev_evt = tgt_event_type[:, t] if teacher_force else top1_evt
            prev_time = tgt_time_bin[:, t] if teacher_force else top1_time
            
        return {
            "event_type": outputs_event,
            "time_bin": outputs_time,
            "actor": outputs_actor,
            "target": outputs_target,
            "domain": outputs_domain
        }
