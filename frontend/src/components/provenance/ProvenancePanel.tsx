import type { APIProvenance } from "../../api/types";
import { Metadata, RawDetails } from "../ui/Primitives";
export function ProvenancePanel({ provenance }: { provenance: APIProvenance }) {
  return (
    <>
      <Metadata data={{ ...provenance }} />
      <RawDetails data={provenance} title="Full provenance response" />
      <p className="notice">
        This response contract does not include an analysis run ID or execution
        timestamp. Session receipt times are labelled separately.
      </p>
    </>
  );
}
