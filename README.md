# 9) Prosignum - sicher und verifizierbare Unterschriftensammlung 

## Approach
Prosignum ist ein **föderal funktionsfähiges, datenschutzwahrendes und kryptografisch verifizierbares System zur elektronischen Unterschriftensammlung**. 
Es kann parallel zum Papierkanal betrieben werden.
Wir legen dabei besonderen Wert auf Sicherheit, Privatsphäre, Verifizierbarkeit, und föderale Anschlussfähigkeit. 

### Designprinzipien
- **Sicherheitsorientiertes Design**: Wir möchten jeden Schritt auf Bedrohungen analysieren und diese bewusst dokumentieren, damit Trade-offs, Vertrauensannahmen sowie Vertrauensgrenzen klar dokumentiert sind.
- **Einfache Implementierbarkeit**: Wir möchten das Verfahren bewusst so konzipieren, dass es ohne hohe organisatorische oder technologische Hürden von allen wichtigen Stakeholdern implementiert werden kann.
- **Mehrstufiger, evolutionärer Ansatz**: Wir schlagen vor, dass in den ersten Iterationen des digitalen Systems möglichst wenig Komplexität (z.B. etablierte statt experimenteller, nicht formell verifizierte, Kryptographie) verwendet wird. Vor allem, da ein Ansatz mit Differential Privacy (z.B. dass die Bundeskanzlei nur noch aggregierte Resultate erhalten würde) gewisse Gesetzesänderungen voraussetzt. Wir fokussieren uns im Hackathon daher auf eine jetzt sinnvolle und möglichst sichere Umsetzung. Die Evolutionsschritte werden im folgenden Abschnitt dargestellt.

### Evolutionäre Entwicklung der Prosignum-Implementierung
Die folgenden Phasen skizzieren wie eine schrittweise Weiterentwicklung des E-Collecting-Systems aussehen könnte. Die Erfahrungen und Ergebnisse jeder Phase würden dabei direkt in die Gestaltung der nachfolgenden Phasen einfliessen. Ob und wie genau diese Phasen durchlaufen werden, lässt sich derzeit nicht abschließend beurteilen.

**Für den Hackathon fokussieren wir uns auf Phase 1, entwickeln gegebenenfalls aber bereits Ansätze für spätere Phasen.**

#### **Phase 1: Pragmatischer Datenschutz**
- **Fokus**: Organisatorische Sicherheit und funktionale Grundlagen ohne komplexe Kryptographie
- **Features**:
  - E-ID Integration für sichere Authentifizierung
  - Digitale Signierung der Unterstützungsbekundung
  - Parallelbetrieb mit Papierkanal
  - Einfache Verifizierung durch Stimmregister
- **Vorteile**: Schnelle Einführung, geringe technische Hürden für Gemeinden

#### **Phase 2: Erweiterte Sicherheit**
- **Fokus**: Verbesserte kryptografische Verfahren
- **Potenzielle Features**:
  - Zero-Knowledge-Proofs (ZKP) für Stimmberechtigung
  - Verteilte Verifizierung durch mehrere Stimmregister
  - Anonymisierte Zwischenstände
  - Post-Quantum-sichere Kryptographieverfahren

#### **Phase 3: Vollständige Privacy-Implementierung**
- **Fokus**: Maximaler Datenschutz mit Differential Privacy
- **Potenzielle Features**:
  - Homomorphe Verschlüsselung der Unterstützungsbekundungen
  - Bundeskanzlei erhält nur aggregierte, anonymisierte Resultate
  - Vollständig verteiltes System ohne Vertrauen in zentrale Instanzen
  - Möglicher Verzicht auf Papierkanal
- **Voraussetzung**: Gesetzesanpassungen, umfassende technische Infrastruktur

Jede Phase baut auf den Erfahrungen der vorherigen auf und ermöglicht ein iteratives Vorgehen mit kontinuierlicher Verbesserung.

### **Gesuchte Ergänzungen fürs Team**
 Um den Ansatz zu stärken, suchen wir Unterstützung vor allem in nicht-technischen Bereichen:
-   **Politisches und staatsrechtliches Know-how** – sowie Wissen zu direktdemokratischen Verfahren, Bundesrecht, Politische Rechte, und institutionellen Abläufen.    
- **User Experience / Accessibility** - Unterstützung in Benutzerfreundlichkeit und Barrierefreiheit.
-   **Kenntnisse der E-ID-Infrastruktur** – technische und organisatorische Einbindung der nationalen E-ID sowie der föderalen Stimmregistersysteme.
-   **Verwaltungs- und Prozesswissen** – Verständnis für föderale Zuständigkeiten, Abläufe auf Gemeinde- und Kantonsebene sowie Schnittstellen zu bestehenden IT-Systemen (z. B. AGOV, allfällige kantonsspezifische Infrastruktur).

## Documentation and Diagrams
`TODO`

### Flowchart: High-level Process
`TODO`

### Sequence Diagram: Detailed Interactions & Data Flows 
`TODO`

## User Experience
`TODO`

## Topics addressed
The following table discusses the topics presented in the [guidelines](https://www.bk.admin.ch/bk/de/home/politische-rechte/e-collecting/aktuelles.html).*

| Topic | (How) is it addressed? |
| -| ------- |
| 1 | PC Website URL, Mobile App QR code, and Paper with QR code provide three entry points. |
| 2 | Encrypted DB stores "Committees: Initiative → vote counts" with connections to Federal Chancellor and Municipality, enabling access to signature counts. |
| 3 | Database explicitly tracks "Committees: Initiative → vote counts", showing attribution of signatures to committees. |
| 4 |  |
| 5 | Swiyu E-ID Login provides authentication. Municipality performs "manual signature check / deduplication" step before returning data to DB. |
| 6 |  |
| 7 | Encrypted DB is used for data storage. |
| 8 | Paper with QR code is included as one of three input channels alongside digital options (PC Website, Mobile App). |
| 9 | Municipality has "Adapter for Electronic Rolls" allowing integration with existing systems. Manual signature check/deduplication supports municipalities without advanced systems. |
| 10 |  |

## Key Strenghts and Weaknesses
`TODO`

### Strengths:
- ...
- ...

### Weaknesses:
- ...
- ...

## Getting Started
`TODO`

*These instructions will get you a copy of the technical prototype (if applicable) up and running on your local machine for development and testing purposes. **If you are not developing a technical prototype, please present or reference your conceptual and/or clickable prototype.***

### Prerequisites

*What things you need to install the software and how to install them.*

### Installation

*A step by step series of examples that tell you how to get a development env running.*

## Contributing

Please read [CONTRIBUTING.md](/CONTRIBUTING.md) for details on our code of conduct.

## Team Members

- Christian Killer / [acuraster](https://github.com/acuraster) (Team-Co-Lead)
- Alessandro de Carli / [dcale](https://github.com/dcale) (Team-Co-Lead)
- Andreas Gassmann / [AndreasGassmann](https://github.com/AndreasGassmann) 
- Lukas Schönbächler / [lukeisontheroad](https://github.com/lukeisontheroad)
- Michelle Fund / [michellefund](https://github.com/michellefund) 
- William Dan / [william-dan](https://github.com/william-dan)
- Hao Wang / [haowangcoder](https://github.com/haowangcoder)

## License

This software is licensed under a AGPL 3.0 License - see the [LICENSE](LICENSE) file for details. Please feel free to [choose any other](https://choosealicense.com/) [Open Source Initiative approved license](https://opensource.org/licenses) (e.g. a permissive license such as [MIT](https://opensource.org/license/mit)). Other content (e.g. text, images, etc.) is licensed under a [Creative Commons CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/deed.de). Exceptions are possible in consultation with the organizers.



