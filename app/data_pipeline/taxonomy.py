"""Statistical taxonomy and Extended 20-per-Trade M3NHF Schedule of Rates (SOR) Feed for Phase 4."""

from typing import Dict, List
from app.domain.enums import MessageIntent, TradeCode
from app.domain.sor_catalog import BASE_M3NHF_SOR_CATALOG, SORItem


# Target statistical proportions grounded in UK Housing Ombudsman Service & Property Tribunal determinations
OMBUDSMAN_INTENT_DISTRIBUTION: Dict[str, float] = {
    MessageIntent.NEW_REPAIR_DEFECT.value: 0.60,          # 60% Responsive property repairs
    MessageIntent.WIP_REPAIR_UPDATE.value: 0.10,          # 10% Chasing open work-in-progress repairs
    MessageIntent.COMPLETED_REPAIR_COMPLAINT.value: 0.10, # 10% Post-repair workmanship / recall complaints
    MessageIntent.CONTRACTOR_SCHEDULING.value: 0.08,      # 8% Appointment booking / rescheduling
    MessageIntent.CONTRACTOR_PAYMENT_INQUIRY.value: 0.05, # 5% Subcontractor invoice / PO payment queries
    MessageIntent.GENERAL_HOUSING_QUERY.value: 0.04,      # 4% Leasehold / service charge / ASB queries
    "INAPPROPRIATE_CONTENT": 0.03,                        # 3% Explicit / rude / abusive submissions purged in Stage 1
}

# Target trade proportions across responsive repairs & completed-job recalls
REPAIR_TRADE_DISTRIBUTION: Dict[TradeCode, float] = {
    TradeCode.PLUM: 0.25,  # Section 19: Plumbing & Heating
    TradeCode.DAMP: 0.20,  # Section 11: Damp, Mould & Specialist Treatments
    TradeCode.JOIN: 0.17,  # Section 12: Joinery & Carpentry
    TradeCode.ROOF: 0.14,  # Section 10: Roofing & Rainwater Goods
    TradeCode.ELEC: 0.14,  # Section 21: Electrical Installations
    TradeCode.PLAS: 0.10,  # Section 16: Plastering, Rendering & Wall Finishes
}


# Additional M3NHF codes per trade (supplementing BASE_M3NHF_SOR_CATALOG to reach 20 codes per trade)
ADDITIONAL_M3NHF_SOR_BY_TRADE: Dict[TradeCode, List[SORItem]] = {
    TradeCode.PLUM: [
        SORItem(
            sor_code="191002",
            trade=TradeCode.PLUM,
            short_description="Renew defective brass stopcock or main internal cold water isolation valve",
            full_specification=(
                "M3NHF Section 19 (191002): Freeze or isolate incoming mains water supply, drain down, remove seized "
                "or leaking 15mm/22mm BS1010 brass stopcock, install new full-bore stopcock, and pressure test."
            ),
            unit_of_measure="NO",
            base_rate_gbp=68.50,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="191015",
            trade=TradeCode.PLUM,
            short_description="Lag exposed domestic cold and hot water pipework with nitrile foam insulation",
            full_specification=(
                "M3NHF Section 19 (191015): Supply and fit Class O closed-cell phenolic/nitrile pipe insulation "
                "sleeving to exposed copper pipework in loft or airing cupboard to prevent freezing."
            ),
            unit_of_measure="M",
            base_rate_gbp=14.20,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="192012",
            trade=TradeCode.PLUM,
            short_description="Clear blocked bath or shower waste pipe and reseal trap assembly",
            full_specification=(
                "M3NHF Section 19 (192012): Remove bath panel, dismantle and rod 40mm bath/shower trap and waste "
                "run to stack, flush clean, renew rubber compression washers, and water-test."
            ),
            unit_of_measure="IT",
            base_rate_gbp=54.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="192018",
            trade=TradeCode.PLUM,
            short_description="Clear blocked internal/external WC soil stack or inspection chamber gully",
            full_specification=(
                "M3NHF Section 19 (192018): Rod and plunge blocked 110mm foul drainage stack or external gully, "
                "restore free flow, and sanitize affected area."
            ),
            unit_of_measure="IT",
            base_rate_gbp=96.00,
            default_sla_priority="3",
        ),
        SORItem(
            sor_code="193004",
            trade=TradeCode.PLUM,
            short_description="Renew pair of wash hand basin or bath pillar taps (hot and cold)",
            full_specification=(
                "M3NHF Section 19 (193004): Isolate supplies, disconnect worn pillar taps, fit new WRAS-approved "
                "quarter-turn ceramic disc lever pillar taps with flexible connectors, and test."
            ),
            unit_of_measure="PR",
            base_rate_gbp=74.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="193010",
            trade=TradeCode.PLUM,
            short_description="Replace faulty kitchen sink monobloc mixer tap including flexible tails",
            full_specification=(
                "M3NHF Section 19 (193010): Isolate hot and cold service valves, remove dripping kitchen mixer tap, "
                "supply and fix new chrome monobloc swivel spout mixer tap with check valves."
            ),
            unit_of_measure="NO",
            base_rate_gbp=82.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="193022",
            trade=TradeCode.PLUM,
            short_description="Rake out and reseal bath or shower tray perimeter with sanitary silicone",
            full_specification=(
                "M3NHF Section 19 (193022): Cut out perished/mouldy sealant around bath or shower tray, degrease "
                "surfaces, fill bath to weight-test, and apply continuous bead of sanitary anti-fungal silicone."
            ),
            unit_of_measure="M",
            base_rate_gbp=28.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="194002",
            trade=TradeCode.PLUM,
            short_description="Replace cracked ceramic WC pan and reconnect to 110mm soil multikwik",
            full_specification=(
                "M3NHF Section 19 (194002): Disconnect cistern and soil pan connector, remove cracked vitreous china "
                "WC pan, bed and screw new BS EN 997 rimless WC pan to floor, and test flush."
            ),
            unit_of_measure="NO",
            base_rate_gbp=138.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="194015",
            trade=TradeCode.PLUM,
            short_description="Renew broken WC syphon or dual-flush push-button drop valve mechanism",
            full_specification=(
                "M3NHF Section 19 (194015): Isolate cistern, sponge out water, replace split diaphragm or jammed "
                "dual-flush cable drop valve, renew doughnut washer if close-coupled, and test."
            ),
            unit_of_measure="NO",
            base_rate_gbp=62.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="194024",
            trade=TradeCode.PLUM,
            short_description="Replace broken heavy-duty thermoplastic WC seat and stainless hinge set",
            full_specification=(
                "M3NHF Section 19 (194024): Remove damaged toilet seat and corroded bolts, sanitize pan rim, "
                "and fit new heavy-duty ergonomic white thermoplastic ring seat with top-fix hinges."
            ),
            unit_of_measure="NO",
            base_rate_gbp=32.50,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="196005",
            trade=TradeCode.PLUM,
            short_description="Vent air from central heating radiators, repressurize filling loop, and balance",
            full_specification=(
                "M3NHF Section 19 (196005): Bleed trapped air from all dwelling radiators, top up sealed heating "
                "circuit to 1.2 bar via braided filling loop, and balance lockshield return temperatures."
            ),
            unit_of_measure="IT",
            base_rate_gbp=46.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="196012",
            trade=TradeCode.PLUM,
            short_description="Replace leaking thermostatic radiator valve (TRV) and lockshield valve",
            full_specification=(
                "M3NHF Section 19 (196012): Drain down heating drop, remove weeping radiator valve and tail, "
                "install new bi-directional angled TRV head and body, refill inhibitor, and bleed."
            ),
            unit_of_measure="NO",
            base_rate_gbp=79.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="196025",
            trade=TradeCode.PLUM,
            short_description="Replace corroded single or double panel convector radiator up to 1200mm",
            full_specification=(
                "M3NHF Section 19 (196025): Isolate valves, remove pin-holed steel panel radiator, hang new "
                "Stelrad K2 double-panel double-convector radiator on wall brackets, reconnect, and dose inhibitor."
            ),
            unit_of_measure="NO",
            base_rate_gbp=195.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="197008",
            trade=TradeCode.PLUM,
            short_description="Renew 3kW copper immersion heater element and rod thermostat in cylinder",
            full_specification=(
                "M3NHF Section 19 (197008): Isolate 20A spur, partial drain hot water cylinder, spanner out burned "
                "27-inch immersion element, fit new Incoloy element with thermal cut-out thermostat, and test."
            ),
            unit_of_measure="NO",
            base_rate_gbp=114.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="197016",
            trade=TradeCode.PLUM,
            short_description="Recharge or replace unvented cylinder expansion vessel and tundish relief valve",
            full_specification=(
                "M3NHF Section 19 (197016): G3-certified service to dripping tundish on unvented hot water cylinder, "
                "recharge potable expansion vessel to 3.0 bar or renew 6-bar temperature/pressure relief valve."
            ),
            unit_of_measure="IT",
            base_rate_gbp=128.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="198010",
            trade=TradeCode.PLUM,
            short_description="Renew leaking washing machine or dishwasher appliance standpipe and valve",
            full_specification=(
                "M3NHF Section 19 (198010): Replace leaking 15mm x 3/4BSP appliance washing machine Quarter-turn "
                "check valve and 40mm vertical upstand trap beneath kitchen worktop."
            ),
            unit_of_measure="NO",
            base_rate_gbp=49.00,
            default_sla_priority="1",
        ),
    ],
    TradeCode.DAMP: [
        SORItem(
            sor_code="111004",
            trade=TradeCode.DAMP,
            short_description="Open external brick pocket and clear bridged cavity wall debris at DPC level",
            full_specification=(
                "M3NHF Section 11 (111004): Carefully remove bricks at base of external cavity wall, extract mortar "
                "snots and wet slumped insulation bridging the DPC, and reinstate brickwork."
            ),
            unit_of_measure="M",
            base_rate_gbp=88.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="111012",
            trade=TradeCode.DAMP,
            short_description="Install terracotta or uPVC telescopic sub-floor airbrick ventilator",
            full_specification=(
                "M3NHF Section 11 (111012): Cut out blocked sub-floor vent below suspended timber floor, insert "
                "cranked telescopic underfloor ventilator sleeve with vermin grille, and point in mortar."
            ),
            unit_of_measure="NO",
            base_rate_gbp=66.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="112022",
            trade=TradeCode.DAMP,
            short_description="Apply breathable silane/siloxane masonry water-repellent cream to external wall",
            full_specification=(
                "M3NHF Section 11 (112022): Wire-brush porous external facing brickwork and roller-apply deep "
                "penetrating breathable water-repellent masonry cream to stop wind-driven rain ingress."
            ),
            unit_of_measure="M2",
            base_rate_gbp=24.50,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="112030",
            trade=TradeCode.DAMP,
            short_description="Install preformed cavity tray with weep vents above leaking window lintel",
            full_specification=(
                "M3NHF Section 11 (112030): Remove outer leaf courses above window head, insert stepped preformed "
                "polypropylene cavity tray with stop ends, rebuild brickwork, and insert perp weep vents."
            ),
            unit_of_measure="M",
            base_rate_gbp=142.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="113005",
            trade=TradeCode.DAMP,
            short_description="Apply 2-coat cementitious waterproof tanking slurry to earth-retaining wall",
            full_specification=(
                "M3NHF Section 11 (113005): Hack off salt-contaminated plaster to bare masonry, dub out hollows, "
                "and brush-apply two coats of crystalline cementitious waterproof tanking slurry."
            ),
            unit_of_measure="M2",
            base_rate_gbp=58.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="113014",
            trade=TradeCode.DAMP,
            short_description="Fix studded HDPE cavity drainage membrane and replaster with renovating plaster",
            full_specification=(
                "M3NHF Section 11 (113014): Mechanically fix 8mm meshed HDPE dimpled damp-proof membrane to wall "
                "with sealed plugs and apply breathable salt-retarding renovating backing plaster."
            ),
            unit_of_measure="M2",
            base_rate_gbp=76.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="114005",
            trade=TradeCode.DAMP,
            short_description="Strip mould-contaminated wallpaper, sterilize wall, and apply biocidal sealer",
            full_specification=(
                "M3NHF Section 11 (114005): Steam-strip black-mould affected lining paper, bag as hazardous waste, "
                "apply HSE-approved biocidal masonry sterilizer, and coat with vapour-permeable anti-mould paint."
            ),
            unit_of_measure="M2",
            base_rate_gbp=34.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="114018",
            trade=TradeCode.DAMP,
            short_description="Install 37.5mm insulated phenolic thermal plasterboard to cold window reveal",
            full_specification=(
                "M3NHF Section 11 (114018): Eliminate thermal bridging condensation on cold external lintel/reveal "
                "by bonding and mechanically fixing insulated vapour-check plasterboard and skimming."
            ),
            unit_of_measure="M2",
            base_rate_gbp=68.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="114025",
            trade=TradeCode.DAMP,
            short_description="Diamond core-drill 107mm hole and install acoustic passive trickle wall vent",
            full_specification=(
                "M3NHF Section 11 (114025): Core-drill through external masonry wall, insert condensation-reducing "
                "hit-and-miss internal diffuser and external cowled weather grille."
            ),
            unit_of_measure="NO",
            base_rate_gbp=94.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="115002",
            trade=TradeCode.DAMP,
            short_description="Replace crushed loft flexible fan ducting with insulated rigid PVC pipework",
            full_specification=(
                "M3NHF Section 11 (115002): Remove waterlogged/kinked flexible foil hose in roof space, install "
                "100mm insulated rigid ducting with condensation trap to tile vent terminal."
            ),
            unit_of_measure="M",
            base_rate_gbp=44.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="115010",
            trade=TradeCode.DAMP,
            short_description="Supply and install loft Positive Input Ventilation (PIV) whole-house unit",
            full_specification=(
                "M3NHF Section 11 (115010): Hang ultra-low-wattage PIV condensation control unit in loft space, "
                "fit fire-rated ceiling diffuser in central landing, and wire to fused spur."
            ),
            unit_of_measure="NO",
            base_rate_gbp=310.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="116004",
            trade=TradeCode.DAMP,
            short_description="Treat wet rot fungal decay in sub-floor timber joist ends with boron paste",
            full_specification=(
                "M3NHF Section 11 (116004): Expose damp floor joist ends, wire brush decayed sapwood, inject "
                "and brush-apply dual-purpose boron/permethrin timber preservative paste."
            ),
            unit_of_measure="M2",
            base_rate_gbp=52.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="116012",
            trade=TradeCode.DAMP,
            short_description="Eradicate Serpula lacrymans (dry rot) mycelium and irrigate surrounding wall",
            full_specification=(
                "M3NHF Section 11 (116012): Cut back timber 600mm beyond visible dry rot fruiting body, drill "
                "and irrigate brickwork with masonry biocide, and wrap new joist ends in DPC."
            ),
            unit_of_measure="M2",
            base_rate_gbp=148.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="117008",
            trade=TradeCode.DAMP,
            short_description="Complete invasive calcium carbide and thermal imaging damp diagnostic survey",
            full_specification=(
                "M3NHF Section 11 (117008): Carry out BRE Digest 245 gravimetric/carbide moisture profiling, "
                "dew-point hygrometer logging, and infrared thermography report under Awaab's Law."
            ),
            unit_of_measure="IT",
            base_rate_gbp=165.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="118003",
            trade=TradeCode.DAMP,
            short_description="Cut out perished external window perimeter mastic and reseal with polysulphide",
            full_specification=(
                "M3NHF Section 11 (118003): Rake out split external sealant allowing rain penetration around window "
                "frame, insert closed-cell foam backer rod, and gun low-modulus sealant."
            ),
            unit_of_measure="M",
            base_rate_gbp=18.50,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="118015",
            trade=TradeCode.DAMP,
            short_description="Install retrofit stainless steel mortar perpend weep vents above ground DPC",
            full_specification=(
                "M3NHF Section 11 (118015): Drill out vertical perpend mortar joints at 450mm centres and insert "
                "insect-baffled cavity drainage weep vents to relieve trapped cavity water."
            ),
            unit_of_measure="NO",
            base_rate_gbp=15.00,
            default_sla_priority="1",
        ),
    ],
    TradeCode.ROOF: [
        SORItem(
            sor_code="101010",
            trade=TradeCode.ROOF,
            short_description="Renew broken or slipped natural Welsh slate roof tiles using copper tingles",
            full_specification=(
                "M3NHF Section 10 (101010): Access pitched roof, remove broken slate fragments, slide in new "
                "500x250mm natural blue/black slate, and secure with 18mm copper strip tingle."
            ),
            unit_of_measure="NO",
            base_rate_gbp=48.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="101018",
            trade=TradeCode.ROOF,
            short_description="Lift and re-bed loose half-round ridge or hip tiles in 3:1 mortar",
            full_specification=(
                "M3NHF Section 10 (101018): Remove storm-loosened ridge tiles, chip off old mortar bed, re-bed in "
                "fibre-reinforced 3:1 sand/cement mortar with mechanical stainless ridge clips."
            ),
            unit_of_measure="M",
            base_rate_gbp=64.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="101025",
            trade=TradeCode.ROOF,
            short_description="Install uPVC interlocking dry-verge end caps to exposed gable roof edge",
            full_specification=(
                "M3NHF Section 10 (101025): Hack off crumbling cement undercloak at gable verge, fix batten end "
                "brackets, and clip weather-tight uPVC dry verge units."
            ),
            unit_of_measure="M",
            base_rate_gbp=55.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="102004",
            trade=TradeCode.ROOF,
            short_description="Patch repair split or blistered 3-layer torch-on mineral felt flat roof",
            full_specification=(
                "M3NHF Section 10 (102004): Sweep off chippings, cut cross in blistered felt, dry deck, prime with "
                "bitumen, and torch-bond newSBS elastomeric mineral cap-sheet patch up to 2m2."
            ),
            unit_of_measure="M2",
            base_rate_gbp=98.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="102012",
            trade=TradeCode.ROOF,
            short_description="Renew EPDM single-ply rubber membrane to flat roof porch or bay window",
            full_specification=(
                "M3NHF Section 10 (102012): Strip failed felt from porch/bay roof, lay 18mm OSB3 deck, bond 1.5mm "
                "Firestone EPDM seamless rubber membrane, and fix perimeter drip trims."
            ),
            unit_of_measure="M2",
            base_rate_gbp=124.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="102020",
            trade=TradeCode.ROOF,
            short_description="Apply cold-applied liquid polyurethane waterproofing to leaking balcony deck",
            full_specification=(
                "M3NHF Section 10 (102020): Clean and prime concrete balcony/walkway slab, embed glass-fibre mat "
                "over cracks, and apply 2-coat elastomeric liquid waterproofing with anti-slip quartz."
            ),
            unit_of_measure="M2",
            base_rate_gbp=86.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="103005",
            trade=TradeCode.ROOF,
            short_description="Renew stepped Code 4 lead flashing and upstand wedges to chimney stack",
            full_specification=(
                "M3NHF Section 10 (103005): Rake out mortar joints on brickwork chimney stack, dress and wedge "
                "new Code 4 milled lead stepped flashing and back-gutter apron, and point with lead sealant."
            ),
            unit_of_measure="M",
            base_rate_gbp=94.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="103014",
            trade=TradeCode.ROOF,
            short_description="Clear and repair leaking GRP or lead valley gutter between roof slopes",
            full_specification=(
                "M3NHF Section 10 (103014): Remove moss and tile debris from roof valley trough, dress splits "
                "with Code 5 lead or Acrypol fibre-reinforced repair compound, and reset cut tiles."
            ),
            unit_of_measure="M",
            base_rate_gbp=78.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="103022",
            trade=TradeCode.ROOF,
            short_description="Repoint weathered chimney stack brickwork and cement-flaunch chimney pots",
            full_specification=(
                "M3NHF Section 10 (103022): Rake out eroded chimney mortar joints to 20mm, repoint, renew cracked "
                "weathering flaunching around clay pots, and fit bird/rain cowl."
            ),
            unit_of_measure="IT",
            base_rate_gbp=185.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="104006",
            trade=TradeCode.ROOF,
            short_description="Replace rotten timber eaves fascia and soffit board in 18mm cellular uPVC",
            full_specification=(
                "M3NHF Section 10 (104006): Unclip guttering, cut out decayed softwood fascia/soffit up to 3m, "
                "treat rafter feet, and nail new white cellular uPVC fascia with vented soffit."
            ),
            unit_of_measure="M",
            base_rate_gbp=72.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="104015",
            trade=TradeCode.ROOF,
            short_description="Push back bottom row of roof tiles and fit eaves felt support trays",
            full_specification=(
                "M3NHF Section 10 (104015): Remove perished sarking felt sagging behind fascia into gutter, slide "
                "rigid PVC eaves protector trays under breathable membrane, and refix eaves tiles."
            ),
            unit_of_measure="M",
            base_rate_gbp=38.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="105004",
            trade=TradeCode.ROOF,
            short_description="Renew broken 112mm half-round uPVC rainwater gutter length and brackets",
            full_specification=(
                "M3NHF Section 10 (105004): Remove cracked or sagging uPVC gutter section, fix new fascia brackets "
                "to correct fall, clip in new 112mm gutter with EPDM rubber union seals, and flow test."
            ),
            unit_of_measure="M",
            base_rate_gbp=36.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="105020",
            trade=TradeCode.ROOF,
            short_description="Replace missing 68mm uPVC rainwater downpipe shoe, clips, and leaf guard",
            full_specification=(
                "M3NHF Section 10 (105020): Secure loose vertical rainwater downpipe to masonry with stand-off "
                "clips, fit bottom discharge shoe into gully grid, and insert wire balloon guard at outlet."
            ),
            unit_of_measure="NO",
            base_rate_gbp=42.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="105028",
            trade=TradeCode.ROOF,
            short_description="Unblock overflowing cast-iron rainwater hopper head and reseal spigot joint",
            full_specification=(
                "M3NHF Section 10 (105028): Clear compacted leaves and silt from communal cast-iron hopper head, "
                "flush downpipe, and seal rear masonry joint to stop damp staining."
            ),
            unit_of_measure="NO",
            base_rate_gbp=58.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="106008",
            trade=TradeCode.ROOF,
            short_description="Replace cracked polycarbonate skylight dome or pitched roof window flashing",
            full_specification=(
                "M3NHF Section 10 (106008): Remove storm-damaged triple-skin polycarbonate rooflight dome or "
                "overhaul Velux perimeter foam seal and aluminium flashing kit."
            ),
            unit_of_measure="NO",
            base_rate_gbp=215.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="107004",
            trade=TradeCode.ROOF,
            short_description="Top up loft insulation with 200mm mineral wool quilt to reach 300mm depth",
            full_specification=(
                "M3NHF Section 10 (107004): Cross-lay 200mm non-combustible glass mineral wool insulation quilt "
                "over ceiling joists while maintaining 50mm eaves ventilation air gap."
            ),
            unit_of_measure="M2",
            base_rate_gbp=16.50,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="107012",
            trade=TradeCode.ROOF,
            short_description="Renew draughty loft access hatch with insulated drop-down trapdoor and seal",
            full_specification=(
                "M3NHF Section 10 (107012): Remove warped plywood loft lid, install Part L compliant insulated "
                "hinged loft access trapdoor with EPDM compression draught seal and pole catch."
            ),
            unit_of_measure="NO",
            base_rate_gbp=96.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="108005",
            trade=TradeCode.ROOF,
            short_description="Emergency make-safe tarpaulin weatherproofing to storm-damaged roof slope",
            full_specification=(
                "M3NHF Section 10 (108005): Attend within 24h emergency SLA, secure heavy-duty reinforced PVC "
                "tarpaulin sheet over missing roof tiles/hole with timber battens to stop active water ingress."
            ),
            unit_of_measure="IT",
            base_rate_gbp=145.00,
            default_sla_priority="3",
        ),
    ],
    TradeCode.JOIN: [
        SORItem(
            sor_code="121002",
            trade=TradeCode.JOIN,
            short_description="Replace damaged internal hollow-core panelled door and transfer latch",
            full_specification=(
                "M3NHF Section 12 (121002): Unhang split internal door, shoot in new 1981x762x35mm moulded 4-panel "
                "door leaf, hang on new 75mm butt hinges, and fit tubular mortice latch and lever handles."
            ),
            unit_of_measure="NO",
            base_rate_gbp=118.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="121015",
            trade=TradeCode.JOIN,
            short_description="Replace or adjust faulty overhead hydraulic fire door closer mechanism",
            full_specification=(
                "M3NHF Section 12 (121015): Remove leaking or slamming overhead door closer on FD30 fire door, "
                "install BS EN 1154 power-size 3 surface closer, and adjust latch speed."
            ),
            unit_of_measure="NO",
            base_rate_gbp=89.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="121024",
            trade=TradeCode.JOIN,
            short_description="Overhaul composite front entrance door multi-point lock and 3-star cylinder",
            full_specification=(
                "M3NHF Section 12 (121024): Replace jammed Gearbox/multipoint espagnolette locking strip on front "
                "entrance door, fit TS007 3-star anti-snap euro cylinder with 3 keys, and align keeps."
            ),
            unit_of_measure="NO",
            base_rate_gbp=146.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="122004",
            trade=TradeCode.JOIN,
            short_description="Replace broken uPVC window espagnolette handle, gearbox, or safety restrictor",
            full_specification=(
                "M3NHF Section 12 (122004): Release jammed uPVC casement window, renew twin-cam espagnolette "
                "locking mechanism, key-locking cranked handle, and child safety restrictor stay."
            ),
            unit_of_measure="NO",
            base_rate_gbp=68.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="122010",
            trade=TradeCode.JOIN,
            short_description="Renew snapped sash cords and balance weights to timber box sash window",
            full_specification=(
                "M3NHF Section 12 (122010): Remove staff and parting beads, take out sliding sashes, re-thread "
                "waxed braided nylon sash cords over brass axle pulleys, balance lead weights, and refit."
            ),
            unit_of_measure="NO",
            base_rate_gbp=134.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="122018",
            trade=TradeCode.JOIN,
            short_description="Replace misted or cracked 24mm double-glazed sealed window unit",
            full_specification=(
                "M3NHF Section 12 (122018): Measure and de-glaze blown/condensated or cracked hermetically sealed "
                "double-glazed unit, install new Planitherm argon-filled safety glass unit, and clip beading."
            ),
            unit_of_measure="M2",
            base_rate_gbp=112.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="122025",
            trade=TradeCode.JOIN,
            short_description="Cut out rotten external timber window sill and splice hardwood section",
            full_specification=(
                "M3NHF Section 12 (122025): Chisel out wet-rotted timber window sill nose, treat bare wood with "
                "preservative, epoxy-splice new Sapele hardwood sill profile with throating drip, and prime."
            ),
            unit_of_measure="M",
            base_rate_gbp=92.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="123004",
            trade=TradeCode.JOIN,
            short_description="Refix or renew loose, split, or creaking tongue-and-groove floorboards",
            full_specification=(
                "M3NHF Section 12 (123004): Lift damaged 18x120mm softwood floorboards, check for pipes/cables "
                "beneath, noggin between joists, and screw down new treated timber flooring."
            ),
            unit_of_measure="M2",
            base_rate_gbp=54.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="123012",
            trade=TradeCode.JOIN,
            short_description="Replace water-damaged 22mm P5 moisture-resistant chipboard floor deck",
            full_specification=(
                "M3NHF Section 12 (123012): Cut out swollen/spongy chipboard flooring around WC or bath, install "
                "50x100mm timber support noggins, and glue/screw 22mm P5 green T&G caberfloor."
            ),
            unit_of_measure="M2",
            base_rate_gbp=76.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="124006",
            trade=TradeCode.JOIN,
            short_description="Renew damaged MDF or softwood torus skirting board or door architrave",
            full_specification=(
                "M3NHF Section 12 (124006): Remove split or missing skirting/architrave, mitre corners, scribe "
                "internal joints, and fix pre-primed 18x94mm moisture-resistant MDF profile."
            ),
            unit_of_measure="M",
            base_rate_gbp=24.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="124015",
            trade=TradeCode.JOIN,
            short_description="Construct removable plywood pipe boxing around exposed soil or heating pipes",
            full_specification=(
                "M3NHF Section 12 (124015): Fix 38x38mm softwood framing battens and 9mm hardwood faced plywood "
                "two-sided pipe casing with brass cups and screws for future maintenance access."
            ),
            unit_of_measure="M",
            base_rate_gbp=45.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="125004",
            trade=TradeCode.JOIN,
            short_description="Renew water-blown 38mm post-formed laminated kitchen worktop and sink cut-out",
            full_specification=(
                "M3NHF Section 12 (125004): Disconnect inset sink, remove swollen chipboard worktop, cut and fit "
                "new 38mm high-pressure laminate worktop with sealed cut-out, aluminium butt joint, and upstand."
            ),
            unit_of_measure="M",
            base_rate_gbp=128.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="125018",
            trade=TradeCode.JOIN,
            short_description="Replace collapsed metal drawer box, runners, and drawer front on kitchen unit",
            full_specification=(
                "M3NHF Section 12 (125018): Remove broken kitchen drawer, supply and screw new heavy-duty soft-close "
                "metal drawer box and roller runners to carcass sides, and transfer drawer front."
            ),
            unit_of_measure="NO",
            base_rate_gbp=56.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="125025",
            trade=TradeCode.JOIN,
            short_description="Replace water-damaged 1000mm kitchen sink base unit carcass and plinth",
            full_specification=(
                "M3NHF Section 12 (125025): Temporarily support worktop, strip out rotten melamine sink base unit, "
                "install new 18mm rigid cam-and-dowel 1000mm base carcass on adjustable legs, and rehang doors."
            ),
            unit_of_measure="NO",
            base_rate_gbp=164.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="126004",
            trade=TradeCode.JOIN,
            short_description="Renew jammed bathroom privacy tubular deadbolt and thumbturn furniture",
            full_specification=(
                "M3NHF Section 12 (126004): Remove faulty bathroom door lock, mortice in new heavy-duty tubular "
                "deadbolt and latch, and fit satin stainless lever handles with emergency coin release."
            ),
            unit_of_measure="NO",
            base_rate_gbp=52.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="126012",
            trade=TradeCode.JOIN,
            short_description="Supply and fit BS3621 5-lever mortice deadlock or security nightlatch",
            full_specification=(
                "M3NHF Section 12 (126012): Chisel out timber door stile, install insurance-approved BS3621 "
                "5-lever mortice deadlock with hardened steel anti-drill plates and boxed striking keep."
            ),
            unit_of_measure="NO",
            base_rate_gbp=98.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="127008",
            trade=TradeCode.JOIN,
            short_description="Emergency board up smashed window or forced entry door with 18mm OSB sheet",
            full_specification=(
                "M3NHF Section 12 (127008): Attend within 24h emergency SLA, clear broken glass shards safely, "
                "and secure opening with 18mm OSB3 security boarding bolted through internal timber clamp bar."
            ),
            unit_of_measure="IT",
            base_rate_gbp=115.00,
            default_sla_priority="3",
        ),
    ],
    TradeCode.ELEC: [
        SORItem(
            sor_code="211010",
            trade=TradeCode.ELEC,
            short_description="Trace earth-leakage fault and reset nuisance tripping RCD on consumer unit",
            full_specification=(
                "M3NHF Section 21 (211010): Carry out insulation resistance and ramp testing on split-load "
                "consumer unit circuits, isolate faulty appliance/circuit leg, and restore power."
            ),
            unit_of_measure="IT",
            base_rate_gbp=88.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="211018",
            trade=TradeCode.ELEC,
            short_description="Replace defective MCB or Type A RCBO circuit breaker in consumer unit",
            full_specification=(
                "M3NHF Section 21 (211018): Safely isolate main switch, remove burned or failing DIN-rail breaker, "
                "fit manufacturer-matched Type B RCBO, torque terminals, and record Zs loop impedance."
            ),
            unit_of_measure="NO",
            base_rate_gbp=76.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="212004",
            trade=TradeCode.ELEC,
            short_description="Renew faulty 1-gang or 2-gang 10AX moulded plate wall light switch",
            full_specification=(
                "M3NHF Section 21 (212004): Isolate lighting circuit, remove arcing or cracked wall switch plate, "
                "re-sleeve switched live conductor, fit new BS EN 60669 plate switch, and test."
            ),
            unit_of_measure="NO",
            base_rate_gbp=38.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="212008",
            trade=TradeCode.ELEC,
            short_description="Replace broken bathroom ceiling pull-cord light switch and cord",
            full_specification=(
                "M3NHF Section 21 (212008): Isolate lighting circuit, remove jammed ceiling pull-cord mechanism, "
                "fit new 6A 2-way ceiling switch with washable hygienic toggle and patress block."
            ),
            unit_of_measure="NO",
            base_rate_gbp=42.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="212022",
            trade=TradeCode.ELEC,
            short_description="Renew 45A double-pole electric cooker control switch unit with 13A socket",
            full_specification=(
                "M3NHF Section 21 (212022): Isolate radial cooker circuit, inspect 6mm/10mm T&E terminations for "
                "overheating, fit new 45A DP cooker switch with neon indicator, and test polarity."
            ),
            unit_of_measure="NO",
            base_rate_gbp=64.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="212030",
            trade=TradeCode.ELEC,
            short_description="Replace 13A switched fused connection unit (spur) for boiler or extractor",
            full_specification=(
                "M3NHF Section 21 (212030): Isolate circuit, replace burnt or damaged switched fused spur unit "
                "with flex outlet, fit appropriate BS1362 cartridge fuse (3A/13A), and test."
            ),
            unit_of_measure="NO",
            base_rate_gbp=48.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="213004",
            trade=TradeCode.ELEC,
            short_description="Renew brittle or heat-damaged 6-inch ceiling pendant lamp holder and rose",
            full_specification=(
                "M3NHF Section 21 (213004): Isolate lighting circuit, remove perished pendant flex and lamp holder, "
                "fit new halo ceiling rose with heat-resistant T2 bayonet drop and LED lamp."
            ),
            unit_of_measure="NO",
            base_rate_gbp=44.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="213012",
            trade=TradeCode.ELEC,
            short_description="Replace failed bathroom Zone 1/2 IP65 sealed LED bulkhead light fitting",
            full_specification=(
                "M3NHF Section 21 (213012): Isolate bathroom lighting, remove faulty fluorescent or LED fitting, "
                "install new 14W IP65 polycarbonate LED circular luminaire, and seal cable gland."
            ),
            unit_of_measure="NO",
            base_rate_gbp=78.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="213020",
            trade=TradeCode.ELEC,
            short_description="Renew external PIR motion-sensor or dusk-to-dawn LED security floodlight",
            full_specification=(
                "M3NHF Section 21 (213020): Access external wall above entrance/garden, replace water-damaged "
                "floodlight with 20W IP65 die-cast LED PIR floodlight, and set lux/time dials."
            ),
            unit_of_measure="NO",
            base_rate_gbp=92.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="214010",
            trade=TradeCode.ELEC,
            short_description="Install mains-wired carbon monoxide (CO) alarm with 10-year lithium backup",
            full_specification=(
                "M3NHF Section 21 (214010): Supply and fix BS EN 50291 mains-powered interlinked Carbon Monoxide "
                "detector in room containing gas boiler/appliance and issue minor works certificate."
            ),
            unit_of_measure="NO",
            base_rate_gbp=86.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="215004",
            trade=TradeCode.ELEC,
            short_description="Replace failed 8.5kW or 9.5kW instantaneous electric shower unit",
            full_specification=(
                "M3NHF Section 21 (215004): Isolate 40A/45A shower circuit and cold mains, remove burnt-out electric "
                "shower, install multi-entry replacement 8.5kW thermostatic shower unit, and commission."
            ),
            unit_of_measure="NO",
            base_rate_gbp=198.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="215012",
            trade=TradeCode.ELEC,
            short_description="Renew overheated 45A ceiling pull-cord isolator switch for electric shower",
            full_specification=(
                "M3NHF Section 21 (215012): Cut back heat-discoloured 10mm cable insulation, terminate into new "
                "heavy-duty 45A/50A crabtree double-pole ceiling pull switch with mechanical flag."
            ),
            unit_of_measure="NO",
            base_rate_gbp=68.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="216004",
            trade=TradeCode.ELEC,
            short_description="Replace faulty central heating room thermostat or 2-channel programmer",
            full_specification=(
                "M3NHF Section 21 (216004): Isolate heating spur, replace unresponsive wall thermostat or digital "
                "7-day heating/hot-water timer on standard backplate, and test boiler firing."
            ),
            unit_of_measure="NO",
            base_rate_gbp=96.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="216014",
            trade=TradeCode.ELEC,
            short_description="Overhaul Economy 7 storage heater thermal cut-out link and input thermostat",
            full_specification=(
                "M3NHF Section 21 (216014): Isolate off-peak and peak supplies, remove storage heater front cover, "
                "reset or replace blown thermal fuse link and charge controller, and vacuum dust."
            ),
            unit_of_measure="NO",
            base_rate_gbp=84.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="217006",
            trade=TradeCode.ELEC,
            short_description="Repair or replace faulty flat door-entry intercom handset and buzzer",
            full_specification=(
                "M3NHF Section 21 (217006): Test low-voltage communal audio door entry wiring, replace defective "
                "wall handset in tenant hallway, and verify two-way speech and door lock release."
            ),
            unit_of_measure="NO",
            base_rate_gbp=74.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="218004",
            trade=TradeCode.ELEC,
            short_description="Renew or re-terminate 10mm main equipotential earth bonding clamp to gas/water",
            full_specification=(
                "M3NHF Section 21 (218004): Clean copper pipework within 600mm of meter/stopcock, fit BS951 safety "
                "earth clamp with 10mm2 green/yellow conductor, and verify <0.05 ohm continuity."
            ),
            unit_of_measure="NO",
            base_rate_gbp=56.00,
            default_sla_priority="2",
        ),
        SORItem(
            sor_code="219002",
            trade=TradeCode.ELEC,
            short_description="Carry out EICR electrical safety inspection and circuit fault diagnosis",
            full_specification=(
                "M3NHF Section 21 (219002): Complete BS7671 Electrical Installation Condition Report testing across "
                "dwelling circuits to diagnose intermittent fault, issuing C1/C2/C3 schedule."
            ),
            unit_of_measure="IT",
            base_rate_gbp=160.00,
            default_sla_priority="1",
        ),
    ],
    TradeCode.PLAS: [
        SORItem(
            sor_code="161008",
            trade=TradeCode.PLAS,
            short_description="Apply PVA bond and 2mm multi-finish plaster re-skim to rough wall up to 10m2",
            full_specification=(
                "M3NHF Section 16 (161008): Scrape loose nibs from wall after wallpaper removal, seal with grit/PVA "
                "slurry, and trowel 2-coat Thistle Multi-Finish plaster skim to smooth decorative standard."
            ),
            unit_of_measure="M2",
            base_rate_gbp=28.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="161015",
            trade=TradeCode.PLAS,
            short_description="Dub out and flush-plaster masonry chases after electrical rewiring or pipework",
            full_specification=(
                "M3NHF Section 16 (161015): Damp down cable/pipe chases, fill flush with Hardwall/Browning undercoat "
                "plaster over galvanized capping, scrim tape, and feather finish skim."
            ),
            unit_of_measure="M",
            base_rate_gbp=22.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="161022",
            trade=TradeCode.PLAS,
            short_description="Fix galvanized thin-coat angle bead to damaged wall corner and replaster reveal",
            full_specification=(
                "M3NHF Section 16 (161022): Knock off crushed plaster on window reveal or external pillar corner, "
                "plumb stainless/galvanized angle bead in dabs, and plaster both returns."
            ),
            unit_of_measure="M",
            base_rate_gbp=34.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="162002",
            trade=TradeCode.PLAS,
            short_description="Encapsulate and skim over non-asbestos textured (Artex) ceiling finish",
            full_specification=(
                "M3NHF Section 16 (162002): Verify asbestos-free register, knock off high stipple peaks, apply "
                "Blue Grit bonding primer, and apply 3mm 2-coat smooth plaster skim."
            ),
            unit_of_measure="M2",
            base_rate_gbp=32.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="162015",
            trade=TradeCode.PLAS,
            short_description="Cut out and patch-repair small access hole in plasterboard ceiling up to 0.5m2",
            full_specification=(
                "M3NHF Section 16 (162015): Square off plumber's access hole in ceiling, insert timber batten "
                "cleats above, screw in 12.5mm plasterboard patch, scrim joints, and flush skim."
            ),
            unit_of_measure="IT",
            base_rate_gbp=68.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="162024",
            trade=TradeCode.PLAS,
            short_description="Fix 12.5mm Type F fire-rated pink plasterboard to ceiling and tape joints",
            full_specification=(
                "M3NHF Section 16 (162024): Supply and screw 12.5mm Gyproc FireLine board to underside of joists "
                "with staggered joints, fill with intumescent mastic, and skim for 60-min fire resistance."
            ),
            unit_of_measure="M2",
            base_rate_gbp=48.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="163004",
            trade=TradeCode.PLAS,
            short_description="Replace soggy plasterboard behind bath/shower with moisture-resistant tile backer",
            full_specification=(
                "M3NHF Section 16 (163004): Strip loose tiles and rotten plasterboard around bath/shower wet zone, "
                "fix 12mm cementitious waterproof tile backer board to studs, and tank joints."
            ),
            unit_of_measure="M2",
            base_rate_gbp=64.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="163012",
            trade=TradeCode.PLAS,
            short_description="Re-bed and regrout up to 6 loose or cracked ceramic wall splashback tiles",
            full_specification=(
                "M3NHF Section 16 (163012): Carefully remove cracked or hollow ceramic wall tiles, scrape old "
                "adhesive, fix matching 150x150mm white glazed tiles with waterproof adhesive, and grout."
            ),
            unit_of_measure="IT",
            base_rate_gbp=56.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="163020",
            trade=TradeCode.PLAS,
            short_description="Tile full kitchen worktop or bathroom basin splashback area up to 3m2",
            full_specification=(
                "M3NHF Section 16 (163020): Prime wall substrate, set out PVC edge trim, fix ceramic wall tiles "
                "in waterproof dispersion adhesive, grout with mould-resistant grout, and silicone joint."
            ),
            unit_of_measure="M2",
            base_rate_gbp=58.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="164004",
            trade=TradeCode.PLAS,
            short_description="Hack off hollow external sand/cement render and apply 2-coat bellcast render",
            full_specification=(
                "M3NHF Section 16 (164004): Cut out frost-blown external wall render up to 4m2, fix stainless "
                "bellcast drip bead above DPC, and apply scratch coat and waterproofed float top-coat."
            ),
            unit_of_measure="M2",
            base_rate_gbp=62.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="164012",
            trade=TradeCode.PLAS,
            short_description="Patch repair cracked external pebble-dash or roughcast masonry elevation",
            full_specification=(
                "M3NHF Section 16 (164012): Dub out spalled external wall patch, apply polymer-modified buttering "
                "coat, and dash washed 6mm Spar/Shingle aggregate to match existing elevation."
            ),
            unit_of_measure="M2",
            base_rate_gbp=68.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="165004",
            trade=TradeCode.PLAS,
            short_description="Rake out and fill thermal shrinkage cracks in wall plaster and ceiling coving",
            full_specification=(
                "M3NHF Section 16 (165004): Open V-groove along hairline/settlement plaster cracks, apply glass-fibre "
                "scrim tape, fill with Toupret flexible filler, and sand flush."
            ),
            unit_of_measure="M",
            base_rate_gbp=16.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="165010",
            trade=TradeCode.PLAS,
            short_description="Renew detached or water-damaged 127mm paper-faced gypsum coving length",
            full_specification=(
                "M3NHF Section 16 (165010): Remove sagging ceiling coving, score wall/ceiling lines, mitre and bond "
                "new 127mm C-profile gypsum coving with cove adhesive, and fill joints."
            ),
            unit_of_measure="M",
            base_rate_gbp=24.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="166004",
            trade=TradeCode.PLAS,
            short_description="Apply stain-blocking primer and 2 coats white matt emulsion to water-stained ceiling",
            full_specification=(
                "M3NHF Section 16 (166004): Following leak resolution, scrape flaking paint, brush Zinsser BIN/alkali "
                "stain block over brown water rings, and roller 2 coats trade contract matt emulsion."
            ),
            unit_of_measure="M2",
            base_rate_gbp=18.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="167002",
            trade=TradeCode.PLAS,
            short_description="Hack up and relay spalled concrete floor screed patch prior to floor covering",
            full_specification=(
                "M3NHF Section 16 (167002): Break out crumbling floor screed pocket, prime slab with SBR slurry, "
                "and trowel 1:3 sharp sand/cement screed flush with surrounding floor."
            ),
            unit_of_measure="M2",
            base_rate_gbp=54.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="167010",
            trade=TradeCode.PLAS,
            short_description="Pour 3mm latex self-levelling floor compound to uneven kitchen/bathroom subfloor",
            full_specification=(
                "M3NHF Section 16 (167010): Sweep and prime concrete/quarry tile floor with acrylic primer and "
                "trowel protein-free latex smoothing compound ready for sheet vinyl laying."
            ),
            unit_of_measure="M2",
            base_rate_gbp=26.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="168004",
            trade=TradeCode.PLAS,
            short_description="Repair impact damage to metal/timber stud partition wall with acoustic board",
            full_specification=(
                "M3NHF Section 16 (168004): Cut out kicked-in partition wall section, insert timber noggins and "
                "acoustic slab, fix 12.5mm SoundBloc plasterboard, tape, and apply 2-coat skim."
            ),
            unit_of_measure="M2",
            base_rate_gbp=74.00,
            default_sla_priority="1",
        ),
        SORItem(
            sor_code="169002",
            trade=TradeCode.PLAS,
            short_description="Fire-stop service pipe penetrations through compartment wall with intumescent mortar",
            full_specification=(
                "M3NHF Section 16 (169002): Pack mineral rockwool and trowel certificated 2-hour fire-stopping "
                "intumescent gypsum compound around service risers in riser cupboard."
            ),
            unit_of_measure="IT",
            base_rate_gbp=82.00,
            default_sla_priority="2",
        ),
    ],
}


def build_extended_m3nhf_sor_feed() -> Dict[TradeCode, List[SORItem]]:
    """Combines BASE_M3NHF_SOR_CATALOG with ADDITIONAL_M3NHF_SOR_BY_TRADE to yield 20 SOR codes per trade."""
    feed: Dict[TradeCode, List[SORItem]] = {}
    for trade in [
        TradeCode.PLUM,
        TradeCode.DAMP,
        TradeCode.ROOF,
        TradeCode.JOIN,
        TradeCode.ELEC,
        TradeCode.PLAS,
    ]:
        base_items = list(BASE_M3NHF_SOR_CATALOG.get(trade, []))
        seen_codes = {item.sor_code for item in base_items}
        extras = [
            item
            for item in ADDITIONAL_M3NHF_SOR_BY_TRADE.get(trade, [])
            if item.sor_code not in seen_codes
        ]
        combined = (base_items + extras)[:20]
        feed[trade] = combined
    return feed


def get_feed_sors_for_trade(trade: str | TradeCode, max_codes: int = 20) -> List[SORItem]:
    """Returns up to max_codes (bounded to 1..20) SOR items for the requested trade from the extended feed."""
    bounded_limit = max(1, min(int(max_codes), 20))
    trade_enum = trade if isinstance(trade, TradeCode) else TradeCode(str(trade).upper())
    feed = build_extended_m3nhf_sor_feed()
    return list(feed.get(trade_enum, []))[:bounded_limit]
