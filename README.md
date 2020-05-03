
Fraunhofer Institut für Sichere Informationstechnologie
Author: Patrick Singh
Betreuer: Hervais-Clemence Simo Fhom, Prof. Michael Waidner


BEPIS - Description:
BEPIS is an experimental approach on realizing Epsilon-Differential-Privacy as data anonymization technique for
graph database, e.g. Neo4j. It provides a console interface to a running Neo4j-Graph instance and ways to laod data
into the system, as .csv files. Furthermore, it provides ways to query the database and translates these queries to queries
enforcing epsilon-differential-privacy. As being a prove-of-concept implementation as part of my bachelor thesis,
it only provides first-steps into this topic and is therefore just providing a translation for aggregation queries, like counting queries.
We are implementing the sensitivity-based mechanism with elastic sensitivity as an upper boundary to local sensitivity.
Concretely, we are applying a smoothing function on top of local sensitivity to ensure a certain distance to the true database.

