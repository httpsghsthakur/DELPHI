import { CurrentEventInfo } from '../../api/types';
import { mapEventType, mapActor, mapDomain } from '../../utils/formatting';

interface Props {
  event: CurrentEventInfo;
}

export function CurrentEventCard({ event }: Props) {
  const { extracted_event } = event;
  
  return (
    <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
      <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2 flex justify-between items-center">
        <span>Current Event Extraction</span>
        <span className="text-xs font-mono text-slate-500 bg-slate-900 px-2 py-1 rounded">ID: {event.event_id.split('-')[0]}</span>
      </h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-900/50 rounded-md p-3 border border-slate-800">
          <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Action / Event Type</span>
          <span className="text-sm font-medium text-delphi-accent">{mapEventType(extracted_event.event_type)}</span>
        </div>
        
        <div className="bg-slate-900/50 rounded-md p-3 border border-slate-800">
          <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Domain</span>
          <span className="text-sm font-medium text-slate-300">{mapDomain(extracted_event.domain)}</span>
        </div>
        
        <div className="bg-slate-900/50 rounded-md p-3 border border-slate-800">
          <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Actor</span>
          <span className="text-sm font-medium text-slate-300">{mapActor(extracted_event.actor)}</span>
        </div>
        
        <div className="bg-slate-900/50 rounded-md p-3 border border-slate-800">
          <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Target</span>
          <span className="text-sm font-medium text-slate-300">{mapActor(extracted_event.target)}</span>
        </div>
      </div>
    </div>
  );
}
