# E-Collecting Hackathon – Team 1

> This hackathon contributes to laying out different ways on how to implement e-collecting in Switzerland. Proper documentation is key to ensuring that your solution can be understood and evaluated:
>
> 1) **[Mermaid](https://mermaid.js.org/) diagram(s)** showing interactions and data flowing between actors, software and infrastructure components of your solution
> 2) Figma Mockups/wireframes and user flow showing the UX/UI of your solution 
> 3) Explanation of features used (if applicable)
> 4) A requirements file with all packages and versions used (if applicable)
> 5) Environment code to be run (if applicable)


## Approach

*A brief description of your approach.*

## Architecture and Data Flows

*Find below an example for an architecture and a data flow diagram*

```mermaid
---
config:
  layout: elk
---
flowchart LR
 subgraph Bund["Bund"]
        ECollect["E-Collecting System"]
        BFS[("BFS & Adressdaten")]
  end
 subgraph OGD["OGD Plattform"]
        VB[("Volksbegehren")]
        Statistik[("Anonyme Statistik")]
        SPA["SPA-Volksbegehren: Link auf VB"]
  end
 subgraph Kontrollsystem["Einwohnerkontrollsystem"]
        EReg[("Einwohner-Register")]
        UKontrolle[("Unterschriftenkontrolle")]
        SReg[("Stimmregister")]
  end
 subgraph Gemeinde["Gemeinde / Amtsstelle"]
        Kontrollsystem
  end
 subgraph EIDBox["E-ID Umgebung"]
        EID["E-ID"]
        Quittung["Quittung VC / Willensbekundung"]
  end
    Bevoelkerung(["Bevölkerung"]) -- "SEDEX eCH-Standard XYZ4" --> OGD
    BK(["BK"]) -- "SEDEX eCH-Standard XYZ0" --> OGD
    OGD -- "SEDEX eCH-Standard XYZ2" --> Statistik
    OGD -- 3a --> Gemeinde
    OGD -- 3b --> BK
    OGD -- 3c --> Bevoelkerung
    Gemeinde -- "SEDEX eCH-Standard XYZ1" --> ECollect
    Gemeinde -- "SEDEX eCH-Standard XYZ3" --> ECollect
    ECollect --> BFS
    Buerger(["Bürgerin"]) --> EID & Quittung & Uebogen["Unterschriftenbogen (Papier)"]
    EID -- 5c --> ECollect
    Quittung -- 5d --> ECollect
    Komitee(["Komitee"]) --> Uebogen
    Komitee -- 6a --> Uebogen
    Komitee -- 6b --> Gemeinde
    Komitee -- 6c --> UebogenCert["Unterschriftenbogen (Papier) + Bescheinigung"]

```

## Getting Started

*These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.*

### Prerequisites

*What things you need to install the software and how to install them.*

### Installation

*A step by step series of examples that tell you how to get a development env running.*

## Contributing

Please read [CONTRIBUTING.md](/CONTRIBUTING.md) for details on our code of conduct and the process for submitting merge requests.

## Group Members

- First Name (role)
- First Name (role)
- First Name (role)

## License

This project is licensed under MIT License - see the [LICENSE](LICENSE) file for details.
