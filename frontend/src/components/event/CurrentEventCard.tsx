import type { JsonObject } from "../../api/types";
import { CopyButton, EmptyState, Metadata, RawDetails } from "../ui/Primitives";
export function CurrentEventCard({ event }: { event: JsonObject }) {
  if (!Object.keys(event).length)
    return (
      <EmptyState
        compact
        title="No event extraction returned"
        description="Event attributes will be shown when supplied by the model."
      />
    );
  const { embedding, ...attributes } = event;
  return (
    <>
      <div className="section-intro">
        <p>
          Extracted attributes, as returned by the engine. Numeric actor and
          event IDs have no verified label mapping in the API.
        </p>
        {typeof event.event_id === "string" && (
          <CopyButton value={event.event_id} />
        )}
      </div>
      <Metadata data={attributes} />
      {embedding && <RawDetails data={embedding} title="Returned embedding" />}
    </>
  );
}
