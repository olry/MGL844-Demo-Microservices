# Diagrammes d'architecture

Sources PlantUML, syntaxe simple (pas de C4-PlantUML, pas d'includes externes).
Rendu avec l'extension PlantUML de VS Code ou n'importe quel CLI PlantUML.

Lecture du haut vers le bas : on part de la vue utilisateur, on descend
jusqu'aux conteneurs.

| # | Fichier            | Type        | Montre                                                     |
|---|--------------------|-------------|------------------------------------------------------------|
| 1 | `use_case.puml`    | Cas d'usage | ce que l'utilisateur peut faire                            |
| 2 | `sequence.puml`    | Sequence    | flux complet : creation user, NATS, notification           |
| 3 | `component.puml`   | Composants  | services et leurs liens internes (Controllers, Models, Views) |
| 4 | `class.puml`       | Classes     | classes principales de chaque service (MVC)                |
| 5 | `deployment.puml`  | Deploiement | conteneurs docker-compose, volumes, ports                  |
