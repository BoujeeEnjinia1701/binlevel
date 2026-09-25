# BinLevel

**Area:** Smart Cities · **Status:** Concept · **Prototype budget:** about $60 USD · **Difficulty:** 1 of 5

A fill-level sensor for public and communal bins that reports when bins need emptying so collection routes serve full bins, not empty ones.

## Concept rationale

Fill data cuts wasted trips and overflowing bins at the same time.

## Burning platform

Waste collection is a large municipal cost, and overflowing bins harm public health.

## Where it could be used

### By industry

| Industry | Use |
| --- | --- |
| _To be developed_ | |

### By country or region

| Country or region | Why it matters there |
| --- | --- |
| _To be developed_ | |

## What sparked the idea

It came out of a September 2026 review of Design Molecule's applied research areas against the open projects already in the lab. It connects to WasteWise.

## Problem

Fixed collection schedules empty half-full bins while others overflow.

## Concept

A fill-level sensor for public and communal bins that reports when bins need emptying so collection routes serve full bins, not empty ones.

Full design precis: [docs/02-concept.md](docs/02-concept.md)

## Key components

- Ultrasonic or time-of-flight distance sensor
- Microcontroller and LoRa radio
- Battery, multi-year life
- Bin lid mount

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

A project of the [Design Molecule](https://designmolecule.com) lab. Smart cities set.
