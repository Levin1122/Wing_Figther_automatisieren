import time
import cv2
import numpy as np
import pyautogui
import os
import pygetwindow as gw
from skimage.metrics import structural_similarity as ssim

# Pfade zu den Ordnern
screenshot_folder = r"D:\VSC\Wing_Figther_automatisieren\Screenshots"
vergleich_folder = r"D:\VSC\Wing_Figther_automatisieren\Vergleichen"

# Sicherstellen, dass Screenshot-Ordner existiert
os.makedirs(screenshot_folder, exist_ok=True)

# BlueStacks-Fenster finden
def get_bluestacks_window():
    window_name = "BlueStacks App Player"
    bluestacks_window = None

    # Suche nach einem Fenster, das den Fenstertitel enthält
    for window in gw.getWindowsWithTitle(window_name):
        if window_name in window.title:
            bluestacks_window = window
            break

    if not bluestacks_window:
        print("⚠️ BlueStacks nicht gefunden! Stelle sicher, dass es geöffnet ist.")
        exit()

    return bluestacks_window.left, bluestacks_window.top, bluestacks_window.width, bluestacks_window.height

# Hole die Koordinaten des BlueStacks-Fensters und speichere sie global
x, y, width, height = get_bluestacks_window()

# Funktion für Screenshot
def take_screenshot():
    # Angepasste Region für Screenshot
    new_x = x + 315
    new_y = y + 33
    new_width = width - 348
    new_height = height - 33

    screenshot = pyautogui.screenshot(region=(new_x, new_y, new_width, new_height))
    screenshot_path = os.path.join(screenshot_folder, "bluestacks_screenshot.png")
    screenshot.save(screenshot_path)
    print(f"📸 Neuer Screenshot gespeichert: {screenshot_path}")
    return screenshot_path

# Funktion zum Scrollen von unten nach oben
def scroll_down():
    pyautogui.scroll(-500)
    print("🔽 Herunterscrollen durchgeführt!")

# Funktion zum Erkennen und Klicken eines Buttons
def click_button(button_template_path):
    screenshot_path = take_screenshot()  # Neuer Screenshot für aktuelle Ansicht
    screenshot_np = np.array(pyautogui.screenshot(region=(x, y, width, height)))
    screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
    button_template = cv2.imread(button_template_path, 0)

    result = cv2.matchTemplate(screenshot_gray, button_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val > 0.8:
        button_x, button_y = max_loc
        button_center_x = button_x + (button_template.shape[1] // 2)
        button_center_y = button_y + (button_template.shape[0] // 2)
        
        pyautogui.click(button_center_x + x, button_center_y + y)
        print(f"✅ Button '{button_template_path}' gefunden und geklickt!")
        return True
    else:
        print(f"⚠️ Button '{button_template_path}' nicht gefunden!")
        return False

# Funktion zum Vergleichen von Bildern mit SSIM
def compare_images(image1_path, image2_path):
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
    
    # Größen anpassen, falls nötig
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    similarity_index = ssim(img1, img2)
    return similarity_index

# Funktion zur Symbolerkennung mit Template Matching und Flexibilität (Sammelzentrum)
def find_buttons(screen_image, templates):
    button_positions = []

    # Lade das Screenshot-Bild als NumPy-Array
    screen_image_np = cv2.imread(screen_image, cv2.IMREAD_GRAYSCALE)
    
    for template_path in templates:
        button_Sammelzentrum_templates = cv2.imread(template_path, 0)
        result = cv2.matchTemplate(screen_image_np, button_Sammelzentrum_templates, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Setze eine höhere Sensibilität für die Erkennung
        if max_val > 0.7:  # Toleranzwert für die Ähnlichkeit (anpassen, wenn nötig)
            button_x, button_y = max_loc
            button_center_x = button_x + (button_Sammelzentrum_templates.shape[1] // 2)
            button_center_y = button_y + (button_Sammelzentrum_templates.shape[0] // 2)
            
            # 🟢 Offset-Korrektur anwenden
            button_center_x += 315  # Offset von links
            button_center_y += 33   # Offset von oben

            button_positions.append((button_center_x, button_center_y))
    
    return button_positions

# Funktion zum Klicken von Sammelzentrum-Buttons
def click_sammelzentrum_buttons(x, y, width, height):
    screenshot_path = take_screenshot()
    button_positions = find_buttons(screenshot_path, button_Sammelzentrum_templates)
    
    # Wenn Buttons gefunden wurden, klicke sie
    if button_positions:
        for position in button_positions:
            adjusted_x = position[0] + x
            adjusted_y = position[1] + y
            pyautogui.click(adjusted_x, adjusted_y)
            print(f"✅ Button bei {position} geklickt!")
            time.sleep(1)  # Kurze Pause nach jedem Klick
    else:
        print("⚠️ Keine Sammelzentrum-Buttons gefunden!")

# Bildschirmgröße ermitteln um mittig auf den Bildschirm zu drücken
screen_width, screen_height = pyautogui.size()

# Start-Screenshot erstellen
screenshot_path = take_screenshot()

# Vergleichsbilder
start_img = os.path.join(vergleich_folder, "Startup_startbuttonklicks.png")
dont_start_img = os.path.join(vergleich_folder, "Startup_dontstartbuttonklicks.png")

# Ähnlichkeiten berechnen
sim_start = compare_images(screenshot_path, start_img)
sim_dont_start = compare_images(screenshot_path, dont_start_img)

print(f"🔍 Ähnlichkeit mit 'Startup_startbuttonklicks.png': {sim_start:.2f}")
print(f"🔍 Ähnlichkeit mit 'Startup_dontstartbuttonklicks.png': {sim_dont_start:.2f}")

# Alle Button Pfade
#Immerwiederkommende Buttons
button_Zuruck = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Zuruck_Button.png"
button_Sweep = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Sweep_Button.png"
button_Fortsetzen = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Fortsetzen_Button.png"
button_Schliessen = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Schliessen_Button.png"
#Start Buttons
button_StartZuruck = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Start_Zuruck_Button.png"
button_StartAbholen = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Start_Abholen_Button.png"
button_StartSchnelleGewinne = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Start_Schnelle-Gewinne_Button.png"
button_StartKostenlos = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Start_Kostenlos_Button.png"
button_AbholenKlein = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Start_Abholen-klein_Button.png"
#Store Buttons
button_Store = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Store_Button.png"
button_StorePaket = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Store_Paket_Button.png"
button_StorePaketGratis = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Paket_Gratis_Button.png"
#Tagesevent Buttons
button_Tagesevent = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Button.png"
button_Luftseesimulation = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Luftseesimulation_Button.png"
button_LuftseesimulationGrad3 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Luftseesimulation_Grad3_Button.png"
button_Bombardierung = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Bombardierung_Button.png"
button_BombardierungGrad3 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Bombardierung_Grad3_Button.png"
button_StarkeFeindherausforderung = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Starke-Feindherausforderung_Button.png"
button_StarkeFeindherausforderungGrad2 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Starke-Feindherausforderung_Grad2_Button.png"
button_VerlorenesSchlachtfeld = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Verlorenes-Schlachtfeld_Button.png"
button_VerlorenesSchlachtfeldGrad4 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Verlorenes-Schlachtfeld_Grade4_Button.png"
button_EntdeckedasWolkenmeer = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Entdecke-das-Wolkenmeer_Button.png"
button_EntdeckedasWolkenmeerGrad5 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Entdecke-das-Wolkenmeer_Grade5_Button.png"
button_TödlicherAngriff = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Todlicher-Angriff_Button.png"
button_TödlicherAngriffGrad2 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Todlicher-Angriff_Grade2_Button.png"
button_Nachschub = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Tagesevent_Nachschub_Button.png"
button_NachschubGrad5 = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Nachschub_Grad5_Button.png"
#Event Buttons
button_Event = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Event_Button.png"
button_TitanChallenge = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Event_Titan-Challenge_Button.png"
button_TitanChallengeChallenge = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Titan-Challenge_Challenge_Button.png"
button_Sammelzentrum = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Event_Sammelzentrum_Button.png"
button_EndlosesAbenteuer = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Event_Endloses-Abenteuer_Button.png"
button_EndlosesAbenteuerVerbleibend = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Endloses-Abenteuer_Verbleibend_Button.png"
button_Herausforderung = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Event_Herausforderung_Button.png"
button_HerausforderungStarten = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Herausforderung_Starten_Button.png"
button_Entsendung = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Event_Entsendung_Button.png"
button_EntsendungAbholen = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Entsendung_Abholen_Button.png"
#Angriff Buttons
button_Angriff_Hauptkanone = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Hauptkanone_Button.png"
button_Angriff_Hauptkanone_Upgrade = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Hauptkanone_Upgrade_Button.png"
button_Angriff_Rakete = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Rakete_Button.png"
button_Angriff_Rakete_Upgrade = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Rakete_Upgrade_Button.png"
button_Angriff_Nebenkanone = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Nebenkanone_Button.png"
button_Angriff_Bestatigen = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Bestatigen_Button.png"
button_Angriff_Starten = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Starten_Button.png"
button_Angriff_Belohnung = r"D:\VSC\Wing_Figther_automatisieren\Buttons\Angriff_Belohnung-Zuruck_Button.png"

# Beispielhafte Template-Dateipfade
button_Sammelzentrum_templates = [
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Anfangerhandbuch_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Anfangerhandbuch_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Anfangerhandbuch_Level3.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Diamant_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Diamant_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Diamant_Level3.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\EXPKarte_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\EXPKarte_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\EXPKarte_Level3.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Flugzeug_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Flugzeug_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Flugzeug_Level3.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Legierung_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Legierung_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Legierung_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Nanomaterialien_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Nanomaterialien_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Nanomaterialien_Level3.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Nanomaterialien_Level4.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Sterne_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Sterne_Level2.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Sterne_Level3.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Zufallsmodul_Level1.png",
    r"D:\VSC\Wing_Figther_automatisieren\Buttons\Sammelzentrum\Zufallsmodul_Level4.png",
]

# Entscheiden, welche Buttons gedrückt werden sollen
if sim_start > sim_dont_start:
    print("✅ Mehr Ähnlichkeit mit 'Startup_startbuttonklicks.png'. Buttons werden gedrückt!")

    # 1. Abholen-Button
    if click_button(button_StartAbholen):
        print("✅ Start_Abholen_Button gedrückt!")
        time.sleep(2)

    # 2. Start Schnelle Gewinne-Button
    if click_button(button_StartSchnelleGewinne):
        print("✅ Start_Schnelle-Gewinne_Button gedrückt!")
        time.sleep(2)

    # 3. Start Kostenlos-Button
    if click_button(button_StartKostenlos):
        print("✅ Start_Kostenlos_Button gedrückt!")
        time.sleep(2)

    # 4. Start Abholen-Klein-Button 4 Mal
    for _ in range(4):
        if click_button(button_AbholenKlein):
            print("✅ Start_Abholen-klein_Button gedrückt!")
            time.sleep(3)

    # 5. Schließen-Button 2 Mal
    for _ in range(2):
        click_button(button_Schliessen)
        time.sleep(2)
    print("✅ Schliessen_Button 2 mal gedrückt!")

    # 6. Start Zurück-Button
    if click_button(button_StartZuruck):
        print("✅ Start_Zurück_Button gedrückt!")
    else:
        print("⚠️ Start_Zurück_Button nicht gefunden. Der Button wird übersprungen.")
    
    #------------ HIER ist alles ANDERE drin----------------

    # Store_Button klicken
    if click_button(button_Store):
        print("✅ Store_Button gedrückt!")
        time.sleep(2)

    # Store_Paket_Button klicken
    if click_button(button_StorePaket):
        print("✅ Store_Paket_Button gedrückt!")
        time.sleep(2)

    # Paket_Gratis_Button klicken
    if click_button(button_StorePaketGratis):
        print("✅ Paket_Gratis_Button gedrückt!")
        time.sleep(2)

    # Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)



    #------------ HIER OBEN ist alles ANDERE drin----------------

else:
    print("⏭️ Mehr Ähnlichkeit mit 'Startup_dontstartbuttonklicks.png'. Alternative Buttons werden gedrückt.")

    # Store_Button klicken
    '''if click_button(button_Store):
        print("✅ Store_Button gedrückt!")
        time.sleep(2)

    # Store_Paket_Button klicken
    if click_button(button_StorePaket):
        print("✅ Store_Paket_Button gedrückt!")
        time.sleep(2)

    # Paket_Gratis_Button klicken
    if click_button(button_StorePaketGratis):
        print("✅ Paket_Gratis_Button gedrückt!")
        time.sleep(2)

    # Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)'''

    # 7. Tagesevent_Button klicken
    '''if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)

    # Luftseesimulation machen
    # 8. Tagesevent_Luftseesimulation_Button klicken
    if click_button(button_Luftseesimulation):
        print("✅ Luftseesimulation_Button gedrückt!")
        time.sleep(2)

    # 9. Luftseesimulation_Grad3_Button klicken
    if click_button(button_LuftseesimulationGrad3):
        print("✅ Luftseesimulation_Grad3_Button gedrückt!")
        time.sleep(2)

    # 10. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 11. Fortsetzen_Button 2 Mal klicken
    for _ in range(2):
        if click_button(button_Fortsetzen):
            print("✅ Fortsetzen_Button gedrückt!")
            time.sleep(2)

    # 12. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Start_Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 13. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # Bombardierung machen
    # 14. Tagesevent_Bombardierung_Button klicken
    if click_button(button_Bombardierung):
        print("✅ Tagesevent_Bombardierung_Button gedrückt!")
        time.sleep(2)

    # 15. Bombardierung_Grad3_Button klicken
    if click_button(button_BombardierungGrad3):
        print("✅ Luftseesimulation_Grad3_Button gedrückt!")
        time.sleep(2)

    # 16. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 17. Fortsetzen_Button 2 Mal klicken
    for _ in range(2):
        if click_button(button_Fortsetzen):
            print("✅ Fortsetzen_Button gedrückt!")
            time.sleep(2)

    # 18. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Start_Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 19. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # Starke-Feindherausforderung machen
    # 20. Tagesevent_Starke-Feindherausforderung_Button klicken
    if click_button(button_StarkeFeindherausforderung):
        print("✅ Tagesevent_Starke-Feindherausforderung_Button gedrückt!")
        time.sleep(2)

    # 21. Starke-Feindherausforderung_Grad2_Button klicken
    if click_button(button_StarkeFeindherausforderungGrad2):
        print("✅ Luftseesimulation_Grad3_Button gedrückt!")
        time.sleep(2)

    # 22. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 23. Fortsetzen_Button 2 Mal klicken
    for _ in range(2):
        if click_button(button_Fortsetzen):
            print("✅ Fortsetzen_Button gedrückt!")
            time.sleep(2)

    # 24. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 25. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        scroll_down()
        time.sleep(2)

    # Verlorenes-Schlachtfeld machen
    # 26. Tagesevent_Verlorenes-Schlachtfeld_Button klicken
    if click_button(button_VerlorenesSchlachtfeld):
        print("✅ Tagesevent_Verlorenes-Schlachtfeld_Button gedrückt!")
        time.sleep(2)

    # 27. Verlorenes-Schlachtfeld_Grade4_Button klicken
    if click_button(button_VerlorenesSchlachtfeldGrad4):
        print("✅ Verlorenes-Schlachtfeld_Grade4_Button gedrückt!")
        time.sleep(2)

    # 28. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 41. Fortsetzen_Button 1 Mal klicken, weil ich keine Energie mehr habe
    if click_button(button_Fortsetzen):
        print("✅ Fortsetzen_Button gedrückt!")
        time.sleep(2)

    # 42. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(30152) #hier warten bis ich wieder genug energie habe

    # 40. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 41. Fortsetzen_Button 1 Mal klicken, weil ich keine Energie mehr habe
    if click_button(button_Fortsetzen):
        print("✅ Fortsetzen_Button gedrückt!")
        time.sleep(2)

    # 42. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 43. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
    
    # Endecke-das-Wolkenmeer machen
    # 32. Tagesevent_Entdecke-das-Wolkenmeer_Button klicken
    if click_button(button_EntdeckedasWolkenmeer):
        print("✅ Tagesevent_Entdecke-das-Wolkenmeer_Button gedrückt!")
        time.sleep(2)

    # 33. Entdecke-das-Wolkenmeer_Grade5_Button klicken
    if click_button(button_EntdeckedasWolkenmeerGrad5):
        print("✅ Entdecke-das-Wolkenmeer_Grade5_Button gedrückt!")
        time.sleep(2)

    # 34. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 35. Fortsetzen_Button 2 Mal klicken
    for _ in range(2):
        if click_button(button_Fortsetzen):
            print("✅ Fortsetzen_Button gedrückt!")
            time.sleep(2)

    # 36. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 37. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # Tödlicher Angriff machen
    # 38. Tagesevent_Tödlicher-Angriff_Button klicken
    if click_button(button_TödlicherAngriff):
        print("✅ Tagesevent_Tödlicher-Angriff_Button gedrückt!")
        time.sleep(2)

    # 39. Todlicher-Angriff_Grade2_Button klicken
    if click_button(button_TödlicherAngriffGrad2):
        print("✅ Todlicher-Angriff_Grade2_Button gedrückt!")
        time.sleep(2)

    # 40. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 35. Fortsetzen_Button 2 Mal klicken
    for _ in range(2):
        if click_button(button_Fortsetzen):
            print("✅ Fortsetzen_Button gedrückt!")
            time.sleep(2)

    # 36. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 37. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
    
    # Nachschub machen
    # 44. Tagesevent_Nachschub_Button klicken
    if click_button(button_Nachschub):
        print("✅ Tagesevent_Nachschub_Button gedrückt!")
        time.sleep(2)

    # 45. Nachschub_Grad5_Button klicken
    if click_button(button_NachschubGrad5):
        print("✅ Nachschub_Grad5_Button gedrückt!")
        time.sleep(2)

    # 46. Tagesevent_Sweep_Button klicken
    if click_button(button_Sweep):
        print("✅ Tagesevent_Sweep_Button gedrückt!")
        time.sleep(2)

    # 47. Fortsetzen_Button 2 Mal klicken
    for _ in range(2):
        if click_button(button_Fortsetzen):
            print("✅ Fortsetzen_Button gedrückt!")
            time.sleep(2)

    # 48. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 49. Zurück-Button 2 mal drücken
    for _ in range(2):
        if click_button(button_Zuruck):
            time.sleep(2)
        print("✅ Zurück_Button wurde 2 mal gedrückt!")'''

    #EVENTAUFGABEN
    # 50. Event_Button drücken
    '''if click_button(button_Event):
        print("✅ Event_Button gedrückt!")
        time.sleep(2)'''

    #Titan-Challenge machen
    # 51. Event_Titan-Challenge_Button drücken
    '''if click_button(button_TitanChallenge):
        print("✅ Event_Titan-Challenge_Button gedrückt!")
        time.sleep(2)

    # 52. Titan-Challenge_Challenge_Button drücken
    if click_button(button_TitanChallengeChallenge):
        print("✅ Titan-Challenge_Challenge_Button gedrückt!")
        time.sleep(2)

    # 53. Angriff_Hauptkanone_Button drücken
    if click_button(button_Angriff_Hauptkanone):
        print("✅ Angriff_Hauptkanone_Button gedrückt!")
        time.sleep(2)

    # 54. Angriff_Hauptkanone_Upgrade_Button drücken
    if click_button(button_Angriff_Hauptkanone_Upgrade):
        print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
        time.sleep(2)

    # 55. Angriff_Rakete_Button drücken
    if click_button(button_Angriff_Rakete):
        print("✅ Angriff_Rakete_Button gedrückt!")
        time.sleep(2)

    # 56. Angriff_Rakete_Upgrade_Button drücken
    if click_button(button_Angriff_Rakete_Upgrade):
        print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
        time.sleep(2)

    # 57. Angriff_Nebenkanone_Button drücken
    if click_button(button_Angriff_Nebenkanone):
        print("✅ Angriff_Nebenkanone_Button gedrückt!")
        time.sleep(2)

    # 58. Angriff_Bestatigen_Button als vorletzter Schritt
    if click_button(button_Angriff_Bestatigen):
        print("✅ Angriff_Bestatigen_Button gedrückt!")
        time.sleep(2)

    # 59. Angriff_Starten_Button als letzter Schritt
    if click_button(button_Angriff_Starten):
        print("✅ Angriff_Starten_Button gedrückt!")
        time.sleep(69) # Warten bis der Angriff zuende ist

    # 60. button_Angriff_Belohnung als letzter Schritt
    if click_button(button_Angriff_Belohnung):
        print("✅ button_Angriff_Belohnung gedrückt!")
        time.sleep(2)

    # 61. Zurück-Button drücken
    for _ in range(2):
        if click_button(button_Zuruck):
            time.sleep(2)
        print("✅ Zurück_Button wurde 2 mal gedrückt!")'''

    #Sammelzentrum machen
    # 64. Sammelzentrum-Buttons suchen und klicken
    '''click_sammelzentrum_buttons(x, y, width, height)
    time.sleep(1)'''

        # 62. Sammelzentrum_Button drücken
    if click_button(button_Sammelzentrum):
        print("✅ Sammelzentrum_Button gedrückt!")
        time.sleep(2)

    # 63. Mittig auf den Bildschirm drücken
    '''pyautogui.click(screen_width // 2, screen_height // 2 + screen_height // 4)
    print("✅ Sammelzentrum Loot wurde abgeholt")'''

#bei erhalt von den materialien muss einmal auf dem bildschirm gedrückt (funktion hier^^^) werden beim level up auch
#muss man aber eine if else machen um zu überprüfen ob der bildschirm hervorgekommen ist.
#von hier bis 
    # 64. Sammelzentrum_Buttons suchen und klicken (Funktioniert noch nicht ganz)
    click_sammelzentrum_buttons(x, y, width, height)
    time.sleep(1)