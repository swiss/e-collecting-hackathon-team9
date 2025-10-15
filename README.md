# E-Collecting Hackathon – Team 1

> This hackathon contributes to laying out different ways on how to implement e-collecting in Switzerland. Proper documentation is key to ensuring that your solution can be understood and evaluated:
>
> 1) **[Mermaid](https://mermaid.js.org/) diagram(s)** showing interactions and data flowing between actors, software and infrastructure components of your solution
> 2) Figma Mockups/wireframes and user flow showing the user experience of your solution
> 3) Explanation of features used (if applicable)
> 4) A requirements file with all packages and versions used (if applicable)
> 5) Environment code to be run (if applicable)


## Approach

*A brief description of your approach.*

## Architecture and Data Flows

*Find below an example for an architecture and a data flow diagram*

```mermaid

sequenceDiagram
    actor Customer
    participant WebApp as "Web App"
    participant PaymentGateway as "Payment Gateway"
    participant Database
    participant EmailSrv as "Email Server"
    participant Kitchen

    Customer->>WebApp: Browse menu, select items
    Customer->>WebApp: Place order, provide info
    WebApp->>PaymentGateway: Request payment
    PaymentGateway-->>WebApp: Payment success/failure
    alt Payment success
        WebApp->>Database: Store order
        WebApp->>Kitchen: Send order details
        WebApp->>EmailSrv: Send order confirmation
        EmailSrv-->>Customer: Order confirmation email
        Kitchen-->>Customer: Pizza prepared and delivered
    else Payment failure
        WebApp-->>Customer: Show payment failed
    end

```

```mermaid
flowchart TD
    Customer["Customer"]
    WebApp["Web App"]
    PaymentGateway["Payment Gateway"]
    Database["Order Database"]
    EmailSrv["Email Server"]
    Kitchen["Kitchen"]

    Customer-->|Order & Payment Info|WebApp
    WebApp-->|Payment Data|PaymentGateway
    PaymentGateway-->|Payment Response|WebApp
    WebApp-->|Order Data|Database
    WebApp-->|Order Details|Kitchen
    WebApp-->|Confirmation|EmailSrv
    EmailSrv-->|Email|Customer
    Kitchen-->|Status/Delivery|Customer
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

This project is licensed under MIT License - see the [LICENSE](LICENSE) file for details.
