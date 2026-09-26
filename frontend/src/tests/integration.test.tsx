import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import { apiClient } from '../api/client';

// Mock API responses
vi.mock('../api/client', () => ({
  apiClient: {
    getHealth: vi.fn().mockResolvedValue({
      status: 'ok',
      api_version: '1.0.0',
      models_loaded: true,
      temporal_mode: 'strict',
      execution_mode: 'SYNTHETIC',
      dependencies: { database: 'ok' }
    }),
    analyze: vi.fn().mockResolvedValue({
      analysis_id: "test-run-123",
      timestamp: new Date().toISOString(),
      current_event: {
        event_id: "evt-123",
        extracted_event: { event_type: 4, actor: 1, target: 2, domain: 1, spans: {} }
      },
      credibility: {
        source_reliability: 0.8,
        content_credibility: 0.8,
        final_credibility_score: 0.8,
        calibrated: true
      },
      historical_analogues: [
        {
          event_id: "hist-123",
          date: "2020-01-01T00:00Z",
          similarity_score: 0.9,
          event_details: { title: "Past Trade Policy" },
          outcomes: [{ time_offset: "+30 days", description: "Economic boost" }]
        }
      ],
      scenarios: [
        {
          scenario_id: "scen-1",
          title: "Base Case",
          probability: 0.7,
          sequence_score: 0.8,
          generation_length: 5,
          model_version: "1.0",
          events: [
             { event_type: 2, time_to_event_bin: 1, step_index: 0 }
          ]
        }
      ],
      indicators: [
        {
          indicator_id: "ind-1",
          description: "Monitor trade volume",
          expected_event_type: 2,
          time_window: "1-3 months",
          associated_scenario: "scen-1",
          importance: 0.9
        }
      ],
      provenance: {
        prediction_cutoff: "2026-09-01T00:00Z",
        dataset_version: "synthetic-v1",
        tokenizer_version: "v1",
        eventembed_version: "dummy-v1",
        eventnet_version: "v1",
        crednet_version: "v1",
        causalseq_version: "v1",
        retrieval_index: "v1",
        calibration_version: "v1"
      },
      supporting_evidence: [],
      contradictory_evidence: []
    })
  }
}));

describe('SYNTHETIC FRONTEND INTEGRATION TEST', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('runs complete flow: validate -> load -> render', async () => {
    render(<App />);

    // 1. Initial State Check
    expect(screen.getAllByText(/DELPHI/i).length).toBeGreaterThan(0);
    
    // 2. Input Validation (Temporal Leakage)
    const textInput = screen.getByPlaceholderText(/Paste article text/i);
    fireEvent.change(textInput, { target: { value: 'Test article.' } });

    // Set pub date later than cutoff
    // This is tricky with label association without htmlFor in my quick implementation,
    // let's just trigger submit to see the temporal leakage error if we set pub > cutoff
    // Let's rely on the inputs being ordered pubDate then cutoffDate
    const inputs = document.querySelectorAll('input[type="datetime-local"]');
    fireEvent.change(inputs[0], { target: { value: '2026-10-01T00:00' } });
    fireEvent.change(inputs[1], { target: { value: '2026-09-01T00:00' } });
    
    const analyzeBtn = screen.getByRole('button', { name: /Analyze/i });
    fireEvent.click(analyzeBtn);
    
    expect(await screen.findByText(/TEMPORAL LEAKAGE/i)).toBeInTheDocument();

    // 3. Fix temporal validation and submit
    fireEvent.change(inputs[0], { target: { value: '2026-08-01T00:00' } });
    fireEvent.click(analyzeBtn);

    // 4. Verify API called and loading state cleared, results rendered
    await waitFor(() => {
      expect(apiClient.analyze).toHaveBeenCalled();
    });

    // 5. Verify Current Event
    expect(await screen.findByText(/Current Event Extraction/i)).toBeInTheDocument();
    
    // 6. Verify Scenarios
    expect(screen.getByText(/Probability Distribution/i)).toBeInTheDocument();
    expect(screen.getByText(/Base Case/i)).toBeInTheDocument();
    
    // 7. Verify Indicators
    expect(screen.getByText(/Monitor trade volume/i)).toBeInTheDocument();
    
    // 8. Verify Provenance
    expect(screen.getByText(/Analysis Provenance/i)).toBeInTheDocument();
    expect(screen.getByText(/synthetic-v1/i)).toBeInTheDocument();
    
    // 9. Verify System Status
    expect(screen.getByText(/SYSTEM READY/i)).toBeInTheDocument();
  });
});
