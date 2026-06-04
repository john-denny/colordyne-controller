# Colordyne-controller
A small app to control ColorDyne, calibrated tuneable spectrum lights in the imaging lab in University of Galway

## Our setup
The lights are controlled via a DMX interface (a standard that uses the same connector as XLR, but is generally used for stage lighting), which is controllable via usb. The lighting configuration we (University of Galway's Imaging lab) has, uses 24 individually adressable leds. with channels as follows
245


## Index

| DMX Channel | Name       | Wavelength (nm) | D65 Value (0-255) |
| ----------- | ---------- | --------------- | ----------------- |
| **1**       | lime       | 533             | 103               |
| **2**       | RYL B40    | 447             | 211               |
| **3**       | Violet421  | 422             | 131               |
| **4**       | lime       | 530             | 0                 |
| **5**       | DR-660     | 660             | 123               |
| **6**       | Violet405  | 404             | 191               |
| **7**       | pc-Amber   | 597             | 178               |
| **8**       | DR-735     | 735             | 255               |
| **9**       | red orange | 617             | 51                |
| **10**      | lime       | 535             | 183               |
| **11**      | DR-700     | 694             | 218               |
| **12**      | Sky Blue   | 473             | 240               |
| **13**      | NIR-940    | 942             | 0                 |
| **14**      | DR-680     | 677             | 109               |
| **15**      | lime       | 530             | 51                |
| **16**      | pc-Amber   | 596             | 0                 |
| **17**      | cyan 40    | 494             | 186               |
| **18**      | lime       | 533             | 212               |
| **19**      | FR-850     | 851             | 255               |
| **20**      | OS-640     | 636             | 78                |
| **21**      | lime       | 533             | 251               |
| **22**      | green      | 523             | 0                 |
| **23**      | amber      | 593             | 0                 |
| **24**      | lime       | 531             | 255               |