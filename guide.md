# Guide.md: DIY 4.0V Rechargeable Epsom-Salt Lead-Acid Battery Pack

This document provides a comprehensive, step-by-step engineering guide to constructing a safe, rechargeable, non-lithium battery pack from salvaged and household materials. 

This design utilizes a **modified Planté lead-acid chemistry** using a non-corrosive, non-toxic **Epsom salt (Magnesium Sulfate)** electrolyte. To maximize current output (amperage) and capacity (milliamp-hours), this guide utilizes a **porous-pouch electrode design** inside a rugged, compact plastic housing (such as a salvaged plastic marker tube).

---

## Section 1: Electrochemical Theory & Operating Principles

To successfully build and maintain this battery, it is helpful to understand the chemical reactions occurring inside the cell.

### 1. The Classic Planté Cell
In 1859, Gaston Planté invented the first rechargeable lead-acid battery. His original design consisted of two identical sheets of pure lead rolled in a spiral, separated by rubber strips, and submerged in sulfuric acid. 

Initially, two identical sheets of lead have an electrical potential difference of exactly **0.00V** because they are chemically identical. To make it a battery, electrical current must be forced through the plates. This process is called **forming**:
* **The Positive Plate (Anode during charging):** The electrical current forces oxygen to bond with the lead surface, forming a chocolate-brown layer of **Lead Dioxide ($PbO_2$)**.
* **The Negative Plate (Cathode during charging):** The current reduces any oxides back into a highly porous, grey form of pure **spongy lead ($Pb$)**.

Once formed, these two different chemical states ($PbO_2$ and $Pb$) create an electrochemical potential difference of approximately **2.0V** per cell.

### 2. The Epsom-Salt Modification ($MgSO_4$)
Commercial lead-acid batteries use highly corrosive sulfuric acid ($H_2SO_4$) to achieve high current rates. This is extremely hazardous to handle at home. 

In this DIY design, we substitute sulfuric acid with a saturated solution of **Magnesium Sulfate ($MgSO_4 \cdot 7H_2O$)**, commonly known as Epsom salt.
* **Safety Benefit:** Epsom salt is non-corrosive, non-hazardous, and safe for skin contact.
* **Chemical Function:** The magnesium and sulfate ions ($Mg^{2+}$ and $SO_4^{2-}$) provide the ionic conductivity required for charge transfer between the plates, allowing the lead to undergo its reversible oxidation/reduction cycles safely.

---

## Section 2: Safety & Hazard Mitigation (Mandatory Protocols)

Lead is a heavy metal and a potent neurotoxin. It accumulates in the human body over time and can cause severe damage to the nervous system, kidneys, and brain. However, lead can be handled with virtually zero risk if you strictly adhere to the following safety protocols:

### 1. Zero Dust, Zero Fumes
* **NEVER sand, file, grind, or scrape lead.** This creates fine, invisible lead dust. This dust can easily settle on your clothing, tools, and skin, or be suspended in the air where it is easily inhaled or accidentally ingested.
* **NEVER melt lead.** Melting lead requires high heat, which releases invisible, highly toxic lead vapors into the air. 
* **Safe Manipulation:** Lead is one of the softest, most malleable metals on Earth. You can easily cut it using scissors, utility shears, or wire cutters, and shape it by gently hammering it. These cold-shaping methods generate **zero dust and zero fumes**.

### 2. Personal Protective Equipment (PPE) & Clean-Up
* **Gloves:** Always wear disposable nitrile or latex gloves when handling the lead sinkers, wires, or tools used to shape the lead.
* **Hygiene:** Never touch your eyes, nose, or mouth while working. Once finished, remove your gloves carefully, throw them in the trash, and wash your hands thoroughly with soap and warm water.
* **Workspace Isolation:** Perform all lead manipulation on a disposable surface (such as a sheet of cardboard or newspaper). Once finished, fold up the cardboard or newspaper with any small metal scraps inside and dispose of it safely in the trash. Wipe down your tools with a damp paper towel.

---

## Section 3: Tool & Material Procurement

Before starting construction, gather the following tools and salvaged components:

| Component | Function | Sourcing / Salvage Locations |
| :--- | :--- | :--- |
| **Lead Sinkers** | Active Electrodes | Eagle Claw "split-shot" or egg-style lead sinkers (from a tackle box or sporting goods store). Ensure they are lead, not tungsten or tin. |
| **Porous Separator** | Physical Isolation | Non-woven synthetic epilating (waxing) strips. Highly absorbent, chemically inert, and exceptionally strong. |
| **Electrolyte Salt** | Ionic Conductor | 100% Pure Epsom Salt (Magnesium Sulfate). Available at any pharmacy or grocery store. |
| **Gelling Agent** | Electrolyte Binder | Cornstarch (heated slightly to gel) or unflavored gelatin (Knox gelatin) to turn the liquid into a spill-proof paste. |
| **Casing** | Cell Housing | Hollowed-out plastic bodies of thick dry-erase markers, permanent markers, or small plastic cosmetic/pill bottles. |
| **Conductive Wires** | Current Collectors | Bare copper wire (approx. 20 AWG to 24 AWG) salvaged from electrical cables. |
| **Sealant** | Airtight Protection | Leg-wax beads (depilatory hard wax) or clear UV-cured acrylic resin. |
| **Thread** | Compression | Standard polyester or cotton sewing thread to bind the porous pouches. |

---

## Section 4: Phase-by-Phase Fabrication Guide

This section describes the construction of a single **2.0V high-capacity cell**. You will need to build **two** identical cells to chain them together into a 4.0V battery pack.

---

### Phase 1: Porous Lead Pouch Fabrication

Instead of smooth, flat sheets, we will construct a high-surface-area "porous pouch" electrode. This ensures that the saltwater electrolyte can penetrate deep into the lead mass, multiplying your battery's capacity (mAh) and current output.

```text
       Cross-Section of a Finished Porous Pouch
         ┌─────────────────────────────────┐
         │     Sewing Thread Wrapping      │
         │  ┌───────────────────────────┐  │
         │  │  Epilating Strip Pouch    │  │
         │  │  ┌─────────────────────┐  │  │
         │  │  │   Lead Chips/Flakes │  │  │
         │  │  │   [x] [x] [x] [x]   │  │  │
         │  │  │  [x] [ Bare Copper ] │  │  │
         │  │  │   [x] [ Wire Core ] │  │  │
         │  │  │   [x] [x] [x] [x]   │  │  │
         │  │  └─────────────────────┘  │  │
         │  └───────────────────────────┘  │
         └─────────────────────────────────┘
```

1. **Prepare the Work Area:** Lay down a clean sheet of cardboard or newspaper. Put on your protective gloves and safety glasses.
2. **Flatten the Lead:** Select 3 or 4 large lead split-shot sinkers. Place them on the cardboard and tap them gently with a flat-faced hammer until they are flattened into thin sheets roughly the thickness of a piece of cardboard.
3. **Chop the Lead into Flakes:** 
   * Use a pair of household scissors or utility shears to cut the flat lead sheets into long, thin ribbons (about 2mm wide).
   * Turn the ribbons 90 degrees and snip across them to cut them into hundreds of tiny, crinkled squares/flakes (roughly 2mm x 2mm). 
4. **Construct the Separator Pocket:** 
   * Cut a strip of your epilating waxing paper. The strip should be about 3 inches long and 1.5 inches wide.
   * Fold the strip in half lengthwise to create a pocket that is 1.5 inches long and 0.75 inches wide. Solder or glue the outer side edges closed, leaving the top open.
5. **Install the Current Collector Wire:** 
   * Take a piece of bare copper wire (about 4 inches long) and strip 1.5 inches of insulation off the bottom to expose the bare metal.
   * Loop or bend the bare copper end slightly to increase its contact area, and insert it down into the center of your epilating strip pocket.
6. **Pack the Pouch:** 
   * Pour your tiny, crinkled lead flakes into the pocket around the copper wire. Ensure the lead flakes completely surround the bare copper core.
   * Lightly compress the flakes inside the pocket using the flat end of a pencil or a small rod so they are packed densely.
7. **Sew and Compress:** 
   * Wrap standard sewing thread tightly around the outside of the filled pocket from top to bottom, pulling it taut. 
   * Squeezing the pocket tightly forces the individual lead flakes to make solid physical contact with each other and the copper wire core. This creates a single, highly conductive, highly porous lead electrode.
8. **Repeat:** Repeat this process exactly to build a second identical pouch. One will act as your **Positive (+) Pouch** and the other as your **Negative (–) Pouch**.

---

### Phase 2: Electrolyte Gel Preparation

Turning your saltwater into a solid-state gel prevents leaks, stops the lead flakes from shifting, and keeps the moisture permanently trapped around your electrodes.

1. **Prepare the Saturated Solution:** 
   * Heat 100ml of distilled water in a microwave-safe cup until it is warm.
   * Add Epsom salt (Magnesium Sulfate) one spoonful at a time, stirring thoroughly. Keep adding salt until it no longer dissolves and crystals begin to settle at the bottom. This ensures your electrolyte is fully saturated with ions.
2. **Gel the Solution (Using Cornstarch):**
   * Add 1 tablespoon of cornstarch to your warm, saturated Epsom salt solution and stir vigorously to eliminate any lumps.
   * Heat the mixture in the microwave in short **10-second bursts**, stirring in between. 
   * After 20 to 30 seconds of total heating, the starch will polymerize, turning the liquid into a thick, translucent, non-dripping gel paste (similar in consistency to thick gravy or hair gel). Let it cool to room temperature.

---

### Phase 3: Cell Assembly (Side-by-Side Marker Tube Packing)

We will package the two wet pouches side-by-side inside a hollow plastic marker tube to create a highly compact, robust, cylindrical cell.

```text
               Horizontal Cross-Section of Casing
                    ┌──────────────────┐
                    │  Marker Tube     │
                    │  ┌───┐    ┌───┐  │
                    │  │ P │    │ N │  │
                    │  │ o │    │ e │  │
                    │  │ s │    │ g │  │
                    │  │ i │    │ a │  │
                    │  │ t │    │ t │  │
                    │  │ i │    │ i │  │
                    │  │ v │    │ v │  │
                    │  │ e │    │ e │  │
                    │  └───┘    └───┘  │
                    │ [Epsom Salt Gel] │
                    └──────────────────┘
```

1. **Prepare the Casing:** Take a thick, hollow plastic marker tube (or travel pill bottle). Ensure the inside is completely clean and dry.
2. **Soak the Pouches:** Dip both of your finished lead-flake pouches into the warm Epsom salt gel. Gently squeeze them to ensure the gel penetrates deep between the inner lead flakes.
3. **Insert Into Casing:** Slide both wet, gel-saturated pouches side-by-side down into the plastic marker tube.
   * *Safety Check:* Because the lead flakes are securely trapped inside their own tough, non-conductive epilating pouches, the two pouches can touch each other inside the tube, but the lead inside can never physically touch. This prevents any short circuits.
4. **Fill Remaining Gaps:** Use a small stick or syringe to pack extra Epsom salt gel into the tube, filling any remaining empty spaces around the pouches. Leave about **0.25 inches of empty space** at the very top and bottom of the tube for your sealant plugs.

---

### Phase 4: Sealing & Micro-Venting (The Toothpick Trick)

Because charging a lead-acid battery naturally produces microscopic amounts of hydrogen and oxygen gas, you must include a safety vent. Sealing it completely airtight in solid plastic without a vent can cause pressure to build up, cracking your casing or blowing out the seal.

We will use the **toothpick trick** with your melted leg-wax beads (or UV-cured resin) to create a perfect micro-vent:

```text
                  Top Seal Construction
                 ┌────────┴────────┐  ◄── Hard Leg-Wax/Resin Plug
  (+) Wire ──────┼─── [Graphite] ──┼────► (+) Output Wire
                 │   [Gel/Separator]   │
                 └─────────────────────┘
```

1. **Prepare the Toothpick:** Take a wooden toothpick and rub a thin layer of Vaseline or mineral oil over its tip. This ensures the wax will not stick to the wood.
2. **Insert the Vent Guide:** Thread your Positive wire out the top opening of the marker tube, and insert your greased toothpick down through the opening so the tip rests inside the wet gel.
3. **Pour the Sealant:** 
   * Melt your leg-wax beads (or prepare your UV-cured resin).
   * Pour the liquid wax/resin slowly into the top 0.25-inch gap of the marker tube, surrounding the wires and your toothpick.
4. **Cure/Cool the Seal:** 
   * If using **leg wax**, let it cool naturally at room temperature.
   * If using **UV-cured resin**, use your UV light in short **10-second bursts** (with 30 seconds of cooling time in between). This prevents the resin from getting too hot and boiling your wet electrolyte gel.
5. **Extract the Toothpick:** Once the wax or resin is completely rock-hard, use a pair of pliers to gently twist and pull the toothpick straight out. 
   * *The Result:* You will be left with a microscopic, perfectly clean **vent channel** running from the outside air straight down to your wet separator.
6. **Seal the Bottom:** Flip the tube over. Thread your negative wire out the bottom opening. Pour your wax/resin into the bottom 0.25-inch gap and cure it. (You do not need a vent at the bottom; seal this end completely solid).

*You now have a completed, sealed, non-spillable, beautifully packaged **2.0V Gel Cell**! Repeat these steps to build a second identical cell.*

---

### Phase 5: Series Pack Integration (The 4.0V Pack)

To reach the voltage required to run your USB-C boost board, you will chain your two completed cells in series:

```text
 [Cell 1]                              [Cell 2]
  (–)   (+) ──────────────────────────── (–)   (+)
   │                                            │
[Main Negative Wire]                         [Main Positive Wire]
```

1. Place your two completed marker-tube cells side-by-side.
2. Connect the **Positive wire** (exiting the top of Cell 1) directly to the **Negative wire** (exiting the bottom of Cell 2). Solder this connection securely and wrap it in tape.
3. You will be left with two main connection leads:
   * The **Negative wire** of Cell 1 (Main Negative –).
   * The **Positive wire** of Cell 2 (Main Positive +).

Touch your multimeter to these two main wires. Your meter will read **exactly 0.00V** because the raw lead flakes inside the cells are still chemically identical.

---

## Section 5: Electrochemical "Forming" & Conditioning

To turn your raw lead into an active, energy-storing battery pack, you must perform the chemical **forming process**. This involves forcing current through the cells to oxidize the positive plates:

```text
                         Charging Setup
                         [81 Ω Resistor]
                                │
 [5V USB (+)] ──────────────────┴────────► [Cell 1 Positive (+)]
                                           [Cell 1 Negative (–)] ──┐
                                                                   │
                                           [Cell 2 Positive (+)] ◄─┘
                                           [Cell 2 Negative (–)] ──┐
                                                                   │
 [5V USB (–)] ─────────────────────────────────────────────────────┘
```

1. **Connect the Charging Rig:**
   * Connect your **5V USB power supply** positive line through your **$81\ \Omega$ current-limiting resistor** to the Main Positive wire of your battery pack.
   * Connect your **5V USB negative line (GND)** directly to the Main Negative wire of your battery pack.
2. **The First Charge (The Long Soak):** Leave the pack connected to this charger for **8 to 12 hours**. 
   * *What is happening:* The electrical current will slowly force oxygen into the Positive pouches, converting the grey lead flakes into dark-brown **Lead Dioxide ($PbO_2$)**. The negative plates will remain pure lead. You will see small bubbles rising out of the micro-vent holes—this is normal.
3. **The First Discharge (Conditioning):** 
   * Unplug the 5V charger. 
   * Connect your **$330\ \Omega$ resistor** across the battery pack wires to act as a load. 
   * Let the battery drain slowly until the voltage drops to **3.0V** (1.5V per cell).
4. **Repeat the Cycle:** Charge the battery pack again for 6 hours, and drain it again through the resistor.

*By repeating this charge/discharge cycle 3 or 4 times, you are "conditioning" the lead, forcing the chemical reaction deeper into the core of your lead flakes. Each cycle will dramatically increase the battery's overall capacity (mAh) and current output!*

---

## Section 6: Testing, Integration, and Troubleshooting

Once fully formed, your 2-cell series pack will read approximately **3.8V to 4.0V** on your meter, perfectly matching the operating range of your salvaged USB Type-C power bank board.

### 1. Wiring to the USB-C Board
1. Locate the battery input pads on your salvaged USB-C power bank board (usually labeled **B+** and **B-** or **BAT+** and **BAT-**).
2. Solder your battery pack's **Main Positive wire** (from Cell 2) directly to the **B+** pad.
3. Solder your battery pack's **Main Negative wire** (from Cell 1) directly to the **B-** pad.

```text
  [DIY 4.0V Battery Pack]
   (–)               (+)
    │                 │
    │  ┌───────────┐  │
    └──┤ B-     B+ ├──┘
       │  USB-C    │
       │  Board    │
       └─────┬─────┘
             ▼
       [ 5V USB Out ] ───► Power Your Green LED Indicator!
```

### 2. Testing the Output
* Once soldered, the onboard status LEDs of your salvaged USB-C board should light up, showing that it recognizes your battery pack.
* Plug a USB cable into the output of your board. You can connect your custom green LED circuit (the LED + the $330\ \Omega$ resistor) to the 5V output of the USB cable. The board will boost your battery's 4.0V up to a steady 5.0V, lighting up your LED!

### 3. Engineering Troubleshooting Guide:

| Symptom | Probable Cause | Corrective Action |
| :--- | :--- | :--- |
| **0.00V after charging** | Internal short circuit. | Ensure the copper collector wire inside the pouch has not pierced the separator to touch the opposite lead plate. |
| **Voltage sags instantly to 0V under a load** | High internal resistance. | Wrap the outer casing tighter with rubber bands to compress the lead flakes closer together, or add a few drops of water if the gel has dried out during curing. |
| **Rapid bubbling or boiling during charging** | Charging current is too high. | Ensure your $81\ \Omega$ current-limiting resistor is correctly installed on your charging line to keep the current under 40mA. |
| **Capacity (mAh) is extremely low** | Plates are unformed. | Repeat the charge/discharge conditioning cycle 3 to 5 times to build up the lead-dioxide layer on your positive plates. |