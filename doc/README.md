# Architecture Diagrams

PlantUML sources, plain syntax (no C4-PlantUML, no external includes).
Render with the VS Code PlantUML extension or any PlantUML CLI.

| #  | File                                  | Type            | Shows                                                      |
|----|---------------------------------------|-----------------|------------------------------------------------------------|
| 01 | `01-context.puml`                     | Context         | actors and the system as one box                           |
| 02 | `02-container-starter.puml`           | Container       | what is in the repo today (gateway + hello + NATS)         |
| 03 | `03-container-target.puml`            | Container       | the full 5-service target students will build              |
| 04 | `04-event-flow.puml`                  | Subject map     | NATS publishers / subjects / subscribers                   |
| 05 | `05-sequence-saga-happy.puml`         | Sequence        | auction-accept → wallet debit → order create               |
| 06 | `06-sequence-saga-compensation.puml`  | Sequence        | failure paths → wallet refund → auction reopens            |
| 07 | `07-component-service-template.puml`  | Class diagram   | MVC layout inside a service (controllers / views / models) |
| 08 | `08-state-auction.puml`               | State           | auction lifecycle (open → accepted → closed/cancelled)     |
| 09 | `09-deployment-starter.puml`          | Deployment      | docker-compose nodes, networks, ports (current state)      |

The diagrams progress top-down. Start at 01 and read in order.
