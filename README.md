# E-Collecting Hackathon – Team Title

*Over the course of two days, you will develop your solution for collecting electronic signatures for popular initiatives and referendums from A to Z, addressing the topics outlined in the white paper **(add link to updated version)**. Your prototype can be conceptual, clickable, or technical. Either way, you should clearly present the interactions and data flows between actors, software, and infrastructure components over time, as well as the user experience of these actors.*

## Approach

*A brief description of your approach, a link/reference to the detailed description of your approach and what you have already created (if applicable). Please also mention which skills do you need for your team.*

## Documentation and Diagrams

*Together, you will contribute to comparing different ways of how to implement e-collecting in Switzerland from A to Z. As part of the [participatory process](https://www.bk.admin.ch/bk/de/home/politische-rechte/e-collecting/partizipativer_prozess.html), your solutions will be discussed in subsequent workshops and will ultimately be taken into account for the official decision on which option to pursue as a pilot. Proper documentation is key to ensuring that your solution can be understood and evaluated:*

*1) **[Mermaid](https://mermaid.js.org/) diagram(s)** showing interactions and data flows between actors, software and infrastructure components of your solution over time.
2) Mockups/wireframes and user flow showing the user experience of your solution (using e.g. Figma)
3) Explanation of features used (if applicable)
4) A requirements file with all packages and versions used (if applicable)
5) Environment code to be run (if applicable)*

*For your reference, you will find below an example for two diagrams showing interactions and data flowing between actors, software and infrastructure components of ordering a pizza via a third-party delivery website over time. Please replace them with diagrams for your solution.*

### Flowchart: High-level Process

*An overall process flow showing the main steps and system/actor interactions for ordering a pizza online via a delivery website, including software, infrastructure, and handoff to the restaurant and delivery driver.*

```mermaid

flowchart TD
    Customer([Customer])
    DeliverySite("Delivery Website (Web/App)")
    Backend("Website Backend Server")
    OrderDB[(Order Database)]
    Restaurant("Restaurant Order System")
    Driver("Delivery Driver")

    Customer-->|"Place Order (Pizza+Details)"|DeliverySite
    DeliverySite-->|"Send Order Data"|Backend
    Backend-->|"Store Order"|OrderDB
    Backend-->|"Send Order to Restaurant"|Restaurant
    Restaurant-->|"Ack/Confirmation"|Backend
    Backend-->|"Confirmation & ETA"|DeliverySite
    DeliverySite-->|"Show Confirmation"|Customer
    Restaurant-->|"Assign/Notify Delivery"|Driver
    Driver-->|"Pickup & Deliver"|Customer
    Driver-->|"Update Status"|DeliverySite
    DeliverySite-->|"Show Status"|Customer

```

### Sequence Diagram: Detailed Interactions & Data Flows 

*A step-by-step illustration showing how data and requests are exchanged between actors (customer, delivery site, restaurant, infrastructure), and key software components in the order process.*

```mermaid

sequenceDiagram
    actor Customer
    participant WebApp as "Delivery Website (UI)"
    participant Backend as "Backend Server"
    participant DB as "Order Database"
    participant Restaurant as "Restaurant System"
    actor Driver as "Delivery Driver"

    Customer->>WebApp: Browse menu, select pizza (menu data)
    Customer->>WebApp: Submit order (pizza, address, payment info)
    WebApp->>Backend: Create order {pizza, address, payment}
    Backend->>DB: Save order {orderId, customer, items, payment}
    Backend->>Restaurant: API: send order {orderId, items, address}
    Restaurant-->>Backend: Ack/Confirmation {orderId, ETA}
    Backend-->>WebApp: Show confirmation {orderId, ETA}
    WebApp-->>Customer: Order confirmation {orderId, ETA}
    Restaurant->>Driver: Notify driver {pickup, delivery}
    Driver-->>Restaurant: Pickup ack
    Driver->>Customer: Deliver pizza
    Driver->>Backend: Update status {orderId, delivered}
    Backend->>WebApp: Status update {delivered}
    WebApp->>Customer: Show status {delivered}

```

## Getting Started

*These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.*

### Prerequisites

*What things you need to install the software and how to install them.*

### Installation

*A step by step series of examples that tell you how to get a development env running.*

## Contributing

Please read [CONTRIBUTING.md](/CONTRIBUTING.md) for details on our code of conduct.

## Group Members

- First Name (role)
- First Name (role)
- First Name (role)

## License

This software is licensed under a GPL 3.0 License - see the [LICENSE](LICENSE) file for details. Please feel free to [choose any other](https://choosealicense.com/) [Open Source Initiative approved license](https://opensource.org/licenses) (e.g. a permissive license such as [MIT](https://opensource.org/license/mit)). Other content (e.g. text, images, etc.) is licensed under a [Creative Commons CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/deed.de). Exceptions are possible in consultation with the organizers.
