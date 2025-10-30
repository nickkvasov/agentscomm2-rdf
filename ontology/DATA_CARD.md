# Tourism Ontology Data Card

## Summary
The tourism ontology in this repository models attractions, accommodations, transportation, and traveler personas to support multi-agent curation of destination knowledge. It combines base schema elements from the public [Schema.org](https://schema.org) vocabulary with custom SHACL shapes and SWRL rules tailored for validation experiments.

## Motivation
- **Research goal:** Evaluate how ontology-backed validation pipelines improve reliability of collaborative LLM agents.
- **Intended use:** Serve as the backbone for synthetic and real-world RDF datasets in the accompanying experiments and demos.
- **Out-of-scope uses:** Decision automation in safety-critical domains (e.g., medical or legal) without additional auditing.

## Composition
- **Entity coverage:** LodgingBusiness, Restaurant, TouristAttraction, Transportation, and composite classes such as `CoastalFamilyDestination` inferred via SWRL.
- **Attribute coverage:** Ratings, pricing, amenity flags, age restrictions, accessibility tags, and geographic metadata.
- **Constraints:** SHACL shapes encode range checks, mandatory fields, and logical consistency requirements (e.g., mutually exclusive amenities).
- **Sources:** Seed facts curated from public tourism references and synthetic generator scripts (planned in `scripts/`).

## Collection & Maintenance
- **Update process:** Researchers extend RDF Turtle files under `ontology/` and regenerate derived shapes/rules as experiments evolve.
- **Versioning:** Recommend tagging ontology revisions alongside paper experiment checkpoints to maintain reproducibility.
- **Quality control:** Every change is validated through the gateway pipeline before inclusion in the main knowledge graph.

## Ethical Considerations
- **Bias:** Synthetic examples may reflect curator assumptions; evaluations should include sensitivity analyses for demographic attributes.
- **Privacy:** Repository intentionally avoids personally identifiable information. Any integration with user data must add anonymization safeguards.
- **Misuse:** Downstream deployments should not treat inferred classes (e.g., "family-friendly") as definitive without human oversight.

## Licensing & Access
- **License:** Default project license applies (verify compatibility if importing third-party datasets).
- **Accessibility:** Ontology assets are stored as version-controlled Turtle files to facilitate reproducibility and diff review.

## Recommended Documentation Artifacts
- Change log summarizing ontology updates per experiment.
- Scripted exporters that package ontology subsets for publication appendices.
- Validation reports capturing SHACL and SWRL outcomes for each dataset release.
