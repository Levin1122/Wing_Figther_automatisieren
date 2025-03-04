import time
import cv2
from PIL import ImageGrab
import numpy as np
import pyautogui
import os
import pygetwindow as gw
from skimage.metrics import structural_similarity as ssim

# Pfade zu den Ordnern
screenshot_folder = r"Screenshots"
vergleich_folder = r"Vergleichen"

# Sicherstellen, dass Screenshot-Ordner existiert
os.makedirs(screenshot_folder, exist_ok=True)

#Sammelzentrum ---------------------------------------------------------------------------
# Funktion, um Screenshots aufzunehmen NUR FÜR SAMMELZENTRUM
def take_screenshot_Sammelzentrum():
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    screenshot_path = os.path.join(screenshot_folder, "bluestacks_screenshot.png")
    cv2.imwrite(screenshot_path, screenshot_bgr)
    print(f"📸 Neuer Screenshot gespeichert: {screenshot_path}")
    return screenshot_path

# Funktion, um ein Bild in einem Screenshot zu finden
def find_image(template_path, threshold=0.8):
    screenshot = take_screenshot_Sammelzentrum()
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    result = cv2.matchTemplate(cv2.imread(screenshot), template, cv2.TM_CCOEFF_NORMED)
    
    # Positionen finden, die über dem Threshold liegen
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    
    if locations:
        first_location = locations[0]
        h, w = template.shape[:2]
        center_x = first_location[0] + w // 2
        center_y = first_location[1] + h // 2
        return (center_x, center_y)
    
    return None

# Funktion, um die Koordinaten zu finden und zu speichern
def find_and_save_coordinates(image1, image2):
    coord1 = find_image(image1)
    coord2 = find_image(image2)
    
    if coord1 and coord2:
        print(f"✅ Koordinaten gefunden! \n- Erstes Bild: {coord1}\n- Zweites Bild: {coord2}")
        return coord1, coord2
    else:
        print("❌ Nicht alle Bilder wurden gefunden.")
        return None, None

# Funktion, um auf die gefundenen Koordinaten zu klicken
def click_at_coordinates(coord1, coord2):
    if coord1:
        pyautogui.click(coord1)
        print(f"✅ Auf erste Koordinate {coord1} geklickt!")
        time.sleep(2)
    if coord2:
        time.sleep(2)
        pyautogui.click(coord2)
        print(f"✅ Auf zweite Koordinate {coord2} geklickt!")

#---------------------------------------------------------------------------------------------

# BlueStacks-Fenster finden (simpel für mauszeiger einmitten)
def get_bluestacks_windoww():

    for window in gw.getAllTitles():
        if "BlueStacks" in window:
            return gw.getWindowsWithTitle(window)[0]
    return None

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

# Funktion zum Scrollen von oben nach unten
def scroll_up():
    pyautogui.scroll(500)
    print("🔼 Hochscrollen durchgeführt!")

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

        return True
    else:
        print(f"⚠️ Button '{button_template_path}' nicht gefunden!")
        return False

# Funktion zum Vergleichen von Bildern mit SSIM
def compare_images(find_cords1, find_cords2):
    img1 = cv2.imread(find_cords1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(find_cords2, cv2.IMREAD_GRAYSCALE)
    
    # Größen anpassen, falls nötig
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    similarity_index = ssim(img1, img2)
    return similarity_index

# Die Koordinaten
coord1 = (1361, 746) #Sammelzentrum Flugzeug 1
coord2 = (1454, 744) #Sammelzentrum Flugzeug 2

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
        if max_val > 0.6:  # Toleranzwert für die Ähnlichkeit (anpassen, wenn nötig)
            button_x, button_y = max_loc
            button_center_x = button_x + (button_Sammelzentrum_templates.shape[1] // 2)
            button_center_y = button_y + (button_Sammelzentrum_templates.shape[0] // 2)
            
            # 🟢 Offset-Korrektur anwenden
            button_center_x += 315  # Offset von links
            button_center_y += 33   # Offset von oben

            button_positions.append((button_center_x, button_center_y))
    
    return button_positions

# Funktion um Abholbutton zu finden und um ihn 5 mal zu drücken (Entsendung)(immer der oberste)
def find_Top_buttons(screen_image, template_path):
    button_positions = []

    # Lade das Screenshot-Bild als NumPy-Array
    screen_image_np = cv2.imread(screen_image, cv2.IMREAD_GRAYSCALE)
    button_template = cv2.imread(template_path, 0)
    result = cv2.matchTemplate(screen_image_np, button_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > 0.7:  # Toleranzwert für die Ähnlichkeit
        button_x, button_y = max_loc
        button_center_x = button_x + (button_template.shape[1] // 2)
        button_center_y = button_y + (button_template.shape[0] // 2)
        
        # 🟢 Offset-Korrektur anwenden
        button_center_x += 315  # Offset von links
        button_center_y += 33   # Offset von oben
        
        button_positions.append((button_center_x, button_center_y))
    
    # Buttons nach y-Koordinate sortieren (oberster zuerst)
    button_positions.sort(key=lambda pos: pos[1])
    
    return button_positions

# Funktion zum Klicken auf den obersten Button (Entsendung)
def click_top_button(button_template_path, clicks=5):
    screenshot_path = take_screenshot()
    button_positions = find_Top_buttons(screenshot_path, button_template_path)
    
    if button_positions:
        top_button = button_positions[0]  # Oberster Button (kleinste y-Koordinate)
        adjusted_x = top_button[0] + x
        adjusted_y = top_button[1] + y
        
        # Button so oft klicken wie ich in dem click_top_button({Buttonname}, click=angebe) klicken
        for _ in range(clicks):
            pyautogui.click(adjusted_x, adjusted_y)
            print(f"✅ Oberster Button bei {top_button} geklickt!")
            time.sleep(2)  # Wartezeit zwischen den Klicks
        return True
    else:
        print(f"⚠️ Kein Button gefunden für Template: {button_template_path}")
        return False

# Funktion zum Klicken von Sammelzentrum-Buttons
def click_sammelzentrum_buttons(x, y, width, height):
    screenshot_path = take_screenshot()
    button_positions = find_buttons(screenshot_path, button_Sammelzentrum_templates)
    
    # Wenn Buttons gefunden wurden, klicke den ersten
    if button_positions:
        position = button_positions[0]  # Nur den ersten Button nehmen
        adjusted_x = position[0] + x
        adjusted_y = position[1] + y
        pyautogui.click(adjusted_x, adjusted_y)
        print(f"✅ Erster Button bei {position} geklickt!")
        time.sleep(1)  # Kurze Pause nach dem Klick
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

#mauszeiger in die mitte bringen für scroll_down nachdem man zurück gegangen ist
def mauszeiger_mittig():
        # BlueStacks-Fenster holen
    bs_window = get_bluestacks_windoww()
    if bs_window:
        # Koordinaten und Größe des Fensters abrufen
        x, y, width, height = bs_window.left, bs_window.top, bs_window.width, bs_window.height
        
        # Mitte des Fensters berechnen
        middle_x = x + (width // 2)
        middle_y = y + (height // 2)
        
        # Mauszeiger in die Mitte des BlueStacks-Fensters bewegen
        pyautogui.moveTo(middle_x, middle_y)
        print("🎯 Mauszeiger in die Mitte von BlueStacks bewegt!")
    else:
        print("❌ BlueStacks-Fenster nicht gefunden!")

# Alle Button Pfade
#Bottom Navigationsbar Buttons
button_Home = r"Buttons\Home_Button.png"
#Mail Buttons
button_Menu = r"Buttons\Menu_Button.png"
button_Mail = r"Buttons\Mail_Button.png"
button_Mail_Alles_Lesen = r"Buttons\Mail_Alles-lesen_Button.png"
#Immerwiederkommende Buttons
button_Zuruck = r"Buttons\Zuruck_Button.png"
button_Sweep = r"Buttons\Tagesevent_Sweep_Button.png"
button_Fortsetzen = r"Buttons\Fortsetzen_Button.png"
button_Schliessen = r"Buttons\Schliessen_Button.png"
#Start Buttons
button_StartZuruck = r"Buttons\Start_Zuruck_Button.png"
button_StartAbholen = r"Buttons\Start_Abholen_Button.png"
button_StartSchnelleGewinne = r"Buttons\Start_Schnelle-Gewinne_Button.png"
button_StartKostenlos = r"Buttons\Start_Kostenlos_Button.png"
button_AbholenKlein = r"Buttons\Start_Abholen-klein_Button.png"
#Store Buttons
button_Store = r"Buttons\Store_Button.png"
button_StorePaket = r"Buttons\Store_Paket_Button.png"
button_StorePaketGratis = r"Buttons\Paket_Gratis_Button.png"
#Tagesevent Buttons
button_Tagesevent = r"Buttons\Tagesevent_Button.png"
button_Tagesevent_Abbrechen = r"Buttons\Tagesevent_Abbrechen_Button.png"
button_Luftseesimulation = r"Buttons\Tagesevent_Luftseesimulation_Button.png"
button_LuftseesimulationGrad3 = r"Buttons\Luftseesimulation_Grad3_Button.png"
button_LuftseesimulationGrad1 = r"Buttons\Luftseesimulation_Grad1_Button.png"
button_Bombardierung = r"Buttons\Tagesevent_Bombardierung_Button.png"
button_BombardierungGrad3 = r"Buttons\Bombardierung_Grad3_Button.png"
button_BombardierungGrad1 = r"Buttons\Bombardierung_Grad1_Button.png"
button_StarkeFeindherausforderung = r"Buttons\Tagesevent_Starke-Feindherausforderung_Button.png"
button_StarkeFeindherausforderungGrad2 = r"Buttons\Starke-Feindherausforderung_Grad2_Button.png"
button_StarkeFeindherausforderungGrad1 = r"Buttons\Starke-Feindherausforderung_Grad1_Button.png"
button_VerlorenesSchlachtfeld = r"Buttons\Tagesevent_Verlorenes-Schlachtfeld_Button.png"
button_VerlorenesSchlachtfeldGrad4 = r"Buttons\Verlorenes-Schlachtfeld_Grade4_Button.png"
button_VerlorenesSchlachtfeldGrad1 = r"Buttons\Verlorenes-Schlachtfeld_Grade1_Button.png"
button_EntdeckedasWolkenmeer = r"Buttons\Tagesevent_Entdecke-das-Wolkenmeer_Button.png"
button_EntdeckedasWolkenmeerGrad5 = r"Buttons\Entdecke-das-Wolkenmeer_Grade5_Button.png"
button_EntdeckedasWolkenmeerGrad1 = r"Buttons\Entdecke-das-Wolkenmeer_Grade1_Button.png"
button_TödlicherAngriff = r"Buttons\Tagesevent_Todlicher-Angriff_Button.png"
button_TödlicherAngriffGrad2 = r"Buttons\Todlicher-Angriff_Grade2_Button.png"
button_TödlicherAngriffGrad1 = r"Buttons\Todlicher-Angriff_Grade1_Button.png"
button_Nachschub = r"Buttons\Tagesevent_Nachschub_Button.png"
button_NachschubGrad5 = r"Buttons\Nachschub_Grad5_Button.png"
button_NachschubGrad1 = r"Buttons\Nachschub_Grad1_Button.png"
#Event Buttons
button_Event = r"Buttons\Event_Button.png"
button_TitanChallenge = r"Buttons\Event_Titan-Challenge_Button.png"
button_TitanChallengeChallenge = r"Buttons\Titan-Challenge_Challenge_Button.png"
button_Sammelzentrum = r"Buttons\Event_Sammelzentrum_Button.png"
button_Sammelzentrum_Transport = r"Buttons\Sammelzentrum_Transport_Button.png"
button_Sammelzentrum_Bestatigen = r"Buttons\Sammelzentrum_Bestatigen_Button.png"
button_EndlosesAbenteuer = r"Buttons\Event_Endloses-Abenteuer_Button.png"
button_EndlosesAbenteuer_Verbleibend = r"Buttons\Endloses-Abenteuer_Verbleibend_Button.png"
button_EndlosesAbenteuer_Skip = r"Buttons\Endloses-Abenteuer_Skip_Button.png"
button_EndlosesAbenteuer_Bestatigen = r"Buttons\Endloses-Abenteuer_Bestatigen_Button.png"
button_Herausforderung = r"Buttons\Event_Herausforderung_Button.png"
button_Herausforderung_Starten = r"Buttons\Herausforderung_Starten_Button.png"
button_Entsendung = r"Buttons\Event_Entsendung_Button.png"
button_EntsendungAbholen = r"Buttons\Entsendung_Abholen_Button.png"
button_Entsendung_Entsenden = r"Buttons\Entsendung_Entsenden_Button.png"
button_Entsendung_Flugzeug_Hinzufugen = r"Buttons\Entsendung_Flugzeug_Hinzufugen_Button.png"
button_Entsendung_Flugzeug_Wahlen = r"Buttons\Entsendung_Flugzeug_Wahlen_Button.png"
button_Entsendung_Plus = r"Buttons\Entsendung_plus_Button.png"
#Legion Buttons
button_Legion = r"Buttons\Legion_Button.png"
button_Legion_Event = r"Buttons\Legion_Event_Button.png"
button_Legion_Event_Legionsjagd = r"Buttons\Legion_Event_Legionsjagd_Button.png"
button_Legion_Event_Challenge = r"Buttons\Legion_Event_Challenge_Button.png"
button_Legion_Angriff_Zuruck = r"Buttons\Legion_Angriff_Zuruck.png"
#Unico Buttons
button_Cybertron_Held = r"Buttons\Cybertron-Held_Button.png"
button_StarCave_Voyage = r"Buttons\Unico_StarCave-Voyage_Button.png"
button_StarCave_Abholen = r"Buttons\Unico_StarCave_Abholen_Button.png"
button_Unico_Zuruck = r"Buttons\Unico_Zuruck_Button.png"
button_Unico_Zuruck2 = r"Buttons\Unico_Zuruck2_Button.png"
button_UnicoResist_Unicorn = r"Buttons\Unico_Resist-Unicron_Button.png"
button_Unico_Chllenge = r"Buttons\Unico_Challenge_Button.png"
button_Unico_Schiessubung = r"Buttons\Unico_Schiessubung_Button.png"
button_Unico_Schiessubung_Starten = r"Buttons\Unico_Schiessubung_Starten_Button.png"
button_Unico_Schiessubung_Starten_Starten = r"Buttons\Unico_Schiessubung_Starten_Starten_Button.png"
button_Unico_Schiessubung_Bestatigen = r"Buttons\Unico_Schiessubung_Bestatigen_Button.png"
button_Unico_Event_Aufgaben = r"Buttons\Unico_Event_Aufgaben_Button.png"
button_Unico_Event_Aufgaben_Abholen = r"Buttons\Unico_Event_Aufgaben_Abholen_button.png"
#Angriff Buttons
button_Angriff_Hauptkanone = r"Buttons\Angriff_Hauptkanone_Button.png"
button_Angriff_Hauptkanone_Upgrade = r"Buttons\Angriff_Hauptkanone_Upgrade_Button.png"
button_Angriff_Rakete = r"Buttons\Angriff_Rakete_Button.png"
button_Angriff_Rakete_Upgrade = r"Buttons\Angriff_Rakete_Upgrade_Button.png"
button_Angriff_Nebenkanone = r"Buttons\Angriff_Nebenkanone_Button.png"
button_Angriff_Bestatigen = r"Buttons\Angriff_Bestatigen_Button.png"
button_Angriff_Starten = r"Buttons\Angriff_Starten_Button.png"
button_Angriff_Belohnung = r"Buttons\Angriff_Belohnung-Zuruck_Button.png"
#Bilder um Flugzeugkordinaten zu finden
find_cords1 = r"Buttons\find_cords1.png"
find_cords2 = r"Buttons\find_cords2.png"

# Beispielhafte Template-Dateipfade
button_Sammelzentrum_templates = [
    r"Buttons\Sammelzentrum\Anfangerhandbuch_Level1.png",
    r"Buttons\Sammelzentrum\Anfangerhandbuch_Level2.png",
    r"Buttons\Sammelzentrum\Anfangerhandbuch_Level3.png",
    r"Buttons\Sammelzentrum\Diamant_Level1.png",
    r"Buttons\Sammelzentrum\Diamant_Level2.png",
    r"Buttons\Sammelzentrum\Diamant_Level3.png",
    r"Buttons\Sammelzentrum\EXPKarte_Level1.png",
    r"Buttons\Sammelzentrum\EXPKarte_Level2.png",
    r"Buttons\Sammelzentrum\EXPKarte_Level3.png",
    r"Buttons\Sammelzentrum\Flugzeug_Level1.png",
    r"Buttons\Sammelzentrum\Flugzeug_Level2.png",
    r"Buttons\Sammelzentrum\Flugzeug_Level3.png",
    r"Buttons\Sammelzentrum\Legierung_Level1.png",
    r"Buttons\Sammelzentrum\Legierung_Level2.png",
    r"Buttons\Sammelzentrum\Legierung_Level2.png",
    r"Buttons\Sammelzentrum\Nanomaterialien_Level1.png",
    r"Buttons\Sammelzentrum\Nanomaterialien_Level2.png",
    r"Buttons\Sammelzentrum\Nanomaterialien_Level3.png",
    r"Buttons\Sammelzentrum\Nanomaterialien_Level4.png",
    r"Buttons\Sammelzentrum\Sterne_Level1.png",
    r"Buttons\Sammelzentrum\Sterne_Level2.png",
    r"Buttons\Sammelzentrum\Sterne_Level3.png",
    r"Buttons\Sammelzentrum\Zufallsmodul_Level1.png",
    r"Buttons\Sammelzentrum\Zufallsmodul_Level4.png",
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
    



    #STORE machen
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

    # Zurück-Button drücken und Belohnung abholen
    for i in range(2):
        if click_button(button_Zuruck):
            print("✅ Belohnung abgeholt!")
            print("✅ Zurück_Button gedrückt!")
            time.sleep(2)
    



    #MAIL machen
    # Menu_Button drücken
    if click_button(button_Menu):
        print("✅ Menu_Button gedrückt!")
        time.sleep(2)
    
    # Mail_Button drücken
    if click_button(button_Mail):
        print("✅ Mail_Button gedrückt!")
        time.sleep(2)
    
    # Mail_Alles_Lesen_Button drücken
    if click_button(button_Mail_Alles_Lesen):
        print("✅ Mail_Alles_Lesen_Button gedrückt!")
        time.sleep(2)
    
    # Zurück-Button drücken und Belohnung abholen
    for i in range(2):
        if click_button(button_Zuruck):
            print("✅ Belohnung abgeholt!")
            print("✅ Zurück_Button gedrückt!")
            time.sleep(2)




    #Tagesevent machen
    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)

    #LUFTSEESIMULATION machen
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

    # 9. Luftseesimulation_Grad1_Button klicken
    if click_button(button_LuftseesimulationGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 13. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #BOMBARDIERUNG machen
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

    # 17. Abbrechen_Button klicken
    if click_button(button_Tagesevent_Abbrechen):
        print("✅ Abbrechen_Button gedrückt!")
        time.sleep(2)

    # 15. Bombardierung_Grad1_Button klicken
    if click_button(button_BombardierungGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 19. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #EVENTAUFGABEN
    # 50. Event_Button drücken
    if click_button(button_Event):
        print("✅ Event_Button gedrückt!")
        time.sleep(2)

    #TITAN-CHALLENGE machen
    # 51. Event_Titan-Challenge_Button drücken
    if click_button(button_TitanChallenge):
        print("✅ Event_Titan-Challenge_Button gedrückt!")
        time.sleep(3)

    for i in range(2):
        print(f"🔄 Runde {i+1}/2")

        # 52. Titan-Challenge_Challenge_Button drücken
        if click_button(button_TitanChallengeChallenge):
            print("✅ Titan-Challenge_Challenge_Button gedrückt!")
            time.sleep(14)

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

        # 58. Angriff_Bestatigen_Button drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 59. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(75) # Warten bis der Angriff zuende ist

        # 60. button_Angriff_Belohnung drücken
        if click_button(button_Angriff_Belohnung):
            print("✅ Angriff_Belohnung_Button gedrückt!")
            time.sleep(6)

    
    # 61. Zurück_Button drücken
    if click_button(button_Zuruck):
        time.sleep(2)
        print("✅ Zurück_Button gedrückt!")

        




    #HIER NOCH MIT DER ANDEREN SCREENSHOT FUNKTION AUSPROBIEREN (Sammelzentrum_nichtfindbare buttons testen und sie finden lassen.py)!!!!!!!!!!!!!!!!!!!
    #SAMMELZENTRUM machen
    # 62. Sammelzentrum_Button drücken
    '''if click_button(button_Sammelzentrum):
        print("✅ Sammelzentrum_Button gedrückt!")
        time.sleep(2)

    #einmal clicken falls ich Belhonungen einsammeln muss
    mauszeiger_mittig()
    pyautogui.click()
    time.sleep(2)

    # Flag, um zu prüfen, ob die Koordinaten schon gespeichert wurden für die while schleife
    coordinates_saved = False
    coord1, coord2 = None, None

    while True:
        # Überprüfen, ob Sammelzentrum-Buttons gefunden wurden
        screenshot_path = take_screenshot()
        button_positions = find_buttons(screenshot_path, button_Sammelzentrum_templates)

        if not button_positions:
            print("❌ Keine Sammelzentrum-Buttons gefunden. Schleife wird beendet.")
            break

        # 64. Sammelzentrum_Buttons suchen und klicken (Funktioniert noch nicht ganz)
        click_sammelzentrum_buttons(x, y, width, height)
        time.sleep(1)

        # 65. Sammelzentrum_Transport_Button drücken
        if click_button(button_Sammelzentrum_Transport):
            print("✅ Sammelzentrum_Transport_Button gedrückt!")
            time.sleep(2)

        # 67. Auf die Koordinaten klicken von den 2 Flugzeugen
        if not coordinates_saved:
            coord1, coord2 = find_and_save_coordinates(find_cords1, find_cords2)
            if coord1 and coord2:
                coordinates_saved = True
        click_at_coordinates(coord1, coord2)

        # 66. Sammelzentrum_Bestatigen_Button drücken
        if click_button(button_Sammelzentrum_Bestatigen):
            print("✅ Sammelzentrum_Bestatigen_Button gedrückt!")
            time.sleep(2)

    #einmal clicken falls ich Belhonungen einsammeln muss
    pyautogui.click()
    time.sleep(2)

    # Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)'''




    #ENDLOSES ABENTEUER machen
    # 65. EndlosesAbenteuer_Button drücken
    if click_button(button_EndlosesAbenteuer):
        print("✅ EndlosesAbenteuer_Button gedrückt!")
        time.sleep(2)
    
    # 65. EndlosesAbenteuer_Verbleibend_Button drücken
    if click_button(button_EndlosesAbenteuer_Verbleibend):
        print("✅ EndlosesAbenteuer_Verbleibend_Button gedrückt!")
        time.sleep(2)

    # 65. EndlosesAbenteuer_Skip_Button drücken
    if click_button(button_EndlosesAbenteuer_Skip):
        print("✅ EndlosesAbenteuer_Skip_Button gedrückt!")
        time.sleep(2)

    # 65. EndlosesAbenteuer_Bestatigen_Buttonn drücken
    if click_button(button_EndlosesAbenteuer_Bestatigen):
        print("✅ EndlosesAbenteuer_Bestatigen_Button gedrückt!")
        time.sleep(14)

    # 65. Angriff_Bestatigen_Buttonn drücken
    if click_button(button_Angriff_Bestatigen):
        print("✅ Angriff_Bestatigen_Button gedrückt!")
        time.sleep(2)

    # 65. Angriff_Starten_Button drücken
    if click_button(button_Angriff_Starten):
        print("✅ Angriff_Starten_Button gedrückt!")
        time.sleep(2)

    # 1. while-Schleife läuft unendlich, bis sie mit break gestoppt wird
    while True:
        if not click_button(button_Schliessen):
            print("❌ Schliessen_Button nicht mehr gefunden! Breche die Schleife ab.")
            break
        
        # 2. while-Schleife: Button wird wiederholt gedrückt, solange er gefunden wird
        while click_button(button_Schliessen):
            time.sleep(2)
            print("✅ Schliessen_Button wurde wiederholt gedrückt!")

        time.sleep(120)  # Wartezeit nach dem Drücken
        screenshot_path = take_screenshot()

    # 65. Angriff_Bestätigen_Button drücken Um Behlonung einzusammeln
    if click_button(button_Angriff_Bestatigen):
        print("✅ Angriff_Bestätigen_Button gedrückt!")
        time.sleep(2)

    # Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #HERAUSFORDERUNG machen
    # 66. Herausforderung_Button drücken
    if click_button(button_Herausforderung):
        print("✅ Herausforderung_Button gedrückt!")
        time.sleep(2)

    # Schleife, die 5 Mal durchläuft
    for i in range(5):
        print(f"🔄 Runde {i+1}/5")

        time.sleep(9)

        # 66. Herausforderung_Starten_Button drücken
        if click_button(button_Herausforderung_Starten):
            print("✅ Herausforderung_Starten_Button gedrückt!")
            time.sleep(25)

        # 67. Angriff_Hauptkanone_Button drücken
        if click_button(button_Angriff_Hauptkanone):
            print("✅ Angriff_Hauptkanone_Button gedrückt!")
            time.sleep(2)

        # 68. Angriff_Hauptkanone_Upgrade_Button drücken
        if click_button(button_Angriff_Hauptkanone_Upgrade):
            print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 69. Angriff_Rakete_Button drücken
        if click_button(button_Angriff_Rakete):
            print("✅ Angriff_Rakete_Button gedrückt!")
            time.sleep(2)

        # 70. Angriff_Rakete_Upgrade_Button drücken
        if click_button(button_Angriff_Rakete_Upgrade):
            print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Nebenkanone_Button drücken
        if click_button(button_Angriff_Nebenkanone):
            print("✅ Angriff_Nebenkanone_Button gedrückt!")
            time.sleep(2)

        # 72. Angriff_Bestatigen_Button als vorletzter Schritt
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 74. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(55) # Warten bis der Angriff zu Ende ist

        # 75. Abschluss: Angriff_Bestatigen_Button noch einmal drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button (Abschluss) gedrückt!")
            time.sleep(9)

    # Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    mauszeiger_mittig()
    scroll_down()
    time.sleep(2)




    #ENTSENDUNG machen
    # 66. Entsendung_Button drücken
    if click_button(button_Entsendung):
        print("✅ Entsendung_Button gedrückt!")
        time.sleep(2)
    
    # 67. Abholen button 5 mal drücken + 4 mal belohnung abholen
    if click_top_button(button_EntsendungAbholen, clicks=10):
        print("✅ EntsendungAbholen_Button 5-mal gedrückt!")

    # 49. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        scroll_up()
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #LEGIONEVENT
    # 66. Legion_Button drücken
    if click_button(button_Legion):
            print("✅ Legion_Button gedrückt!")
            time.sleep(2)

    # 66. Legion_Event_Button drücken
    if click_button(button_Legion_Event):
            print("✅ Legion_Event_Button gedrückt!")
            time.sleep(2)

    # 66. Legion_Event_Legionsjagd_Button drücken
    if click_button(button_Legion_Event_Legionsjagd):
            print("✅ Legion_Event_Legionsjagd_Button gedrückt!")
            time.sleep(2)

    # Die 3 Legion Event Angriffe machen
    for i in range(3):
        print(f"🔄 Runde {i+1}/3")

        time.sleep(9)

        # 66. Legion_Event_Challenge_Button drücken
        if click_button(button_Legion_Event_Challenge):
                print("✅ Legion_Event_Challenge_Button gedrückt!")
                time.sleep(25)

        # 67. Angriff_Hauptkanone_Button drücken
        if click_button(button_Angriff_Hauptkanone):
            print("✅ Angriff_Hauptkanone_Button gedrückt!")
            time.sleep(2)

        # 68. Angriff_Hauptkanone_Upgrade_Button drücken
        if click_button(button_Angriff_Hauptkanone_Upgrade):
            print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 69. Angriff_Rakete_Button drücken
        if click_button(button_Angriff_Rakete):
            print("✅ Angriff_Rakete_Button gedrückt!")
            time.sleep(2)

        # 70. Angriff_Rakete_Upgrade_Button drücken
        if click_button(button_Angriff_Rakete_Upgrade):
            print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Nebenkanone_Button drücken
        if click_button(button_Angriff_Nebenkanone):
            print("✅ Angriff_Nebenkanone_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Bestatigen_Button drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(60) # warten bis der Angriff beendet ist

        # 71. Legion_Angriff_Zuruck_Button drücken
        if click_button(button_Legion_Angriff_Zuruck):
            print("✅ Legion_Angriff_Zuruck_Button gedrückt!")
            time.sleep(2)

    time.sleep(8)

    # 66. Zurück_Button 2 mal drücken
    for i in range(2):
        if click_button(button_Zuruck):
            print("✅ Zurück_Button gedrückt!")
            time.sleep(2)
    
    # 71. Home_Button drücken
    if click_button(button_Home):
        print("✅ Home_Button gedrückt!")
        time.sleep(2)
    



    #UNICOEVENT machen
    # Cybertron_Held_Button drücken
    if click_button(button_Cybertron_Held):
        print("✅ Cybertron_Held_Button gedrückt!")
        time.sleep(2)

    # StarCave_Voyage_Button drücken
    if click_button(button_StarCave_Voyage):
        print("✅ StarCave_Voyage_Button gedrückt!")
        time.sleep(2)

    # StarCave_Abholen_Button drücken
    if click_button(button_StarCave_Abholen):
        print("✅ StarCave_Abholen_Button gedrückt!")
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)

    # Unico_Zurück_Button drücken
    if click_button(button_Unico_Zuruck):
        print("✅ Unico_Zurück_Button gedrückt!")
        time.sleep(2)

    # UnicoResist_Unicorn_Button drücken
    if click_button(button_UnicoResist_Unicorn):
        print("✅ UnicoResist_Unicorn_Button gedrückt!")
        time.sleep(2)

    # Die 2 Unico Event Angriffe machen
    for i in range(2):
        print(f"🔄 Runde {i+1}/2")

        time.sleep(9)

        # 66. Unico_Chllenge_Button drücken
        if click_button(button_Unico_Chllenge):
                print("✅ Unico_Chllenge_Button gedrückt!")
                time.sleep(25)

        # 67. Angriff_Hauptkanone_Button drücken
        if click_button(button_Angriff_Hauptkanone):
            print("✅ Angriff_Hauptkanone_Button gedrückt!")
            time.sleep(2)

        # 68. Angriff_Hauptkanone_Upgrade_Button drücken
        if click_button(button_Angriff_Hauptkanone_Upgrade):
            print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 69. Angriff_Rakete_Button drücken
        if click_button(button_Angriff_Rakete):
            print("✅ Angriff_Rakete_Button gedrückt!")
            time.sleep(2)

        # 70. Angriff_Rakete_Upgrade_Button drücken
        if click_button(button_Angriff_Rakete_Upgrade):
            print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Nebenkanone_Button drücken
        if click_button(button_Angriff_Nebenkanone):
            print("✅ Angriff_Nebenkanone_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Bestatigen_Button drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(60) # warten bis der Angriff beendet ist

        # 71. Unico_Angriff_Zuruck_Button drücken
        if click_button(button_Legion_Angriff_Zuruck):
            print("✅ Unico_Angriff_Zurück_Button gedrückt!")
            time.sleep(9)

    time.sleep(9)

    # 66. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 66. Unico_Schiessubung-Button drücken
    if click_button(button_Unico_Schiessubung):
        print("✅ Unico_Schiessubung_Button gedrückt!")
        time.sleep(2)

    # Unico 3 mal die Schiessübung machen
    for i in range(3):
        print(f"🔄 Runde {i+1}/3")

        time.sleep(9)

        # 66. Unico_Schiessubung_Starten_Button drücken
        if click_button(button_Unico_Schiessubung_Starten):
            print("✅ Unico_Schiessubung_Starten_Button gedrückt!")
            time.sleep(2)

        # 66. Unico_Schiessubung_Starten_Starten_Button drücken
        if click_button(button_Unico_Schiessubung_Starten_Starten):
            print("✅ Unico_Schiessubung_Starten_Starten_Button gedrückt!")
            time.sleep(2)

        # Warten bis die Schiessübung zuende ist    
        time.sleep(10)

        # 66. Unico_Schiessubung_Bestatigen_Button drücken
        if click_button(button_Unico_Schiessubung_Bestatigen):
            print("✅ Unico_Schiessubung_Bestatigen_Button gedrückt!")
            time.sleep(2)

    # 66. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # StarCave_Voyage_Button drücken
    if click_button(button_StarCave_Voyage):
        print("✅ StarCave_Voyage_Button gedrückt!")
        time.sleep(2)

    # StarCave_Abholen_Button drücken
    if click_button(button_StarCave_Abholen):
        print("✅ StarCave_Abholen_Button gedrückt!")
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)

    # Unico_Zurück_Button drücken
    if click_button(button_Unico_Zuruck):
        print("✅ Unico_Zurück_Button gedrückt!")
        time.sleep(2)

    # 66. Unico_Event_Aufgaben_Button drücken
    if click_button(button_Unico_Event_Aufgaben):
        print("✅ Unico_Event_Aufgaben_Button gedrückt!")
        time.sleep(2)

    # 66. Unico_Event_Aufgaben_Abholen_Button drücken
    if click_button(button_Unico_Event_Aufgaben_Abholen):
        print("✅ Unico_Event_Aufgaben_Abholen_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        pyautogui.click()
        time.sleep(2)
    
    # 66. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 66. Zurück2_Button drücken um zum Home zu kommen
    if click_button(button_Unico_Zuruck2):
        print("✅ Zurück2_Button gedrückt!")
        time.sleep(2)




    #ENERGIE AUFLADEN
    time.sleep(30152) #hier warten bis ich wieder genug energie habe (50)
    #Prüfen ob Schliessen Button da sind und ob Start Zurück Button da sind
    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_StartZuruck):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)




    #STARKE-FEINDHERAUSFORDERUNG machen
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

    # 21. Starke-Feindherausforderung_Grad1_Button klicken
    if click_button(button_StarkeFeindherausforderungGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 25. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #NACHSCHUB machen
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

    # 48. Schließen_Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 45. Nachschub_Grad1_Button klicken
    if click_button(button_NachschubGrad1):
        print("✅ Nachschub_Grad1_Button gedrückt!")
        time.sleep(2)

    # 49. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        scroll_down()
        time.sleep(2)




    #VERLORENES-SCHLACHTFELD machen
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

    # 27. Verlorenes-Schlachtfeld_Grade1_Button klicken
    if click_button(button_VerlorenesSchlachtfeldGrad1):
        print("✅ Verlorenes-Schlachtfeld_Grade1_Button gedrückt!")
        time.sleep(2)

    # 43. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
    



    #ENDECKE-DAS-WOLKENMEER machen
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

    # 33. Entdecke-das-Wolkenmeer_Grade1_Button klicken
    if click_button(button_EntdeckedasWolkenmeerGrad1):
        print("✅ Entdecke-das-Wolkenmeer_Grade1_Button gedrückt!")
        time.sleep(2)

    # 37. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #TÖDLICHER ANGRIFF machen
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

    # 39. Todlicher-Angriff_Grade1_Button klicken
    if click_button(button_TödlicherAngriffGrad1):
        print("✅ Todlicher-Angriff_Grade1_Button gedrückt!")
        time.sleep(2)

    # 37. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        scroll_up()
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)



    time.sleep(3020) #hier warten bis ich wieder genug energie habe (5)
    #Prüfen ob Schliessen Button da sind und ob Start Zurück Button da sind
    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_StartZuruck):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)
    


    
    #BOMBARDIERUNG machen
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

    # 17. Abbrechen_Button klicken
    if click_button(button_Tagesevent_Abbrechen):
        print("✅ Abbrechen_Button gedrückt!")
        time.sleep(2)

    # 18. Schließen-Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Start_Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 15. Bombardierung_Grad1_Button klicken
    if click_button(button_BombardierungGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 19. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

else:
    print("⏭️ Mehr Ähnlichkeit mit 'Startup_dontstartbuttonklicks.png'. Alternative Buttons werden gedrückt.")

    #STORE machen
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

    # Zurück-Button drücken und Belohnung abholen
    for i in range(2):
        if click_button(button_Zuruck):
            print("✅ Belohnung abgeholt!")
            print("✅ Zurück_Button gedrückt!")
            time.sleep(2)
    



    #MAIL machen
    # Menu_Button drücken
    if click_button(button_Menu):
        print("✅ Menu_Button gedrückt!")
        time.sleep(2)
    
    # Mail_Button drücken
    if click_button(button_Mail):
        print("✅ Mail_Button gedrückt!")
        time.sleep(2)
    
    # Mail_Alles_Lesen_Button drücken
    if click_button(button_Mail_Alles_Lesen):
        print("✅ Mail_Alles_Lesen_Button gedrückt!")
        time.sleep(2)
    
    # Zurück-Button drücken und Belohnung abholen
    for i in range(2):
        if click_button(button_Zuruck):
            print("✅ Belohnung abgeholt!")
            print("✅ Zurück_Button gedrückt!")
            time.sleep(2)




    #Tagesevent machen
    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)

    #LUFTSEESIMULATION machen
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

    # 9. Luftseesimulation_Grad1_Button klicken
    if click_button(button_LuftseesimulationGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 13. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #BOMBARDIERUNG machen
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

    # 17. Abbrechen_Button klicken
    if click_button(button_Tagesevent_Abbrechen):
        print("✅ Abbrechen_Button gedrückt!")
        time.sleep(2)

    # 15. Bombardierung_Grad1_Button klicken
    if click_button(button_BombardierungGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 19. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #EVENTAUFGABEN
    # 50. Event_Button drücken
    if click_button(button_Event):
        print("✅ Event_Button gedrückt!")
        time.sleep(2)

    #TITAN-CHALLENGE machen
    # 51. Event_Titan-Challenge_Button drücken
    if click_button(button_TitanChallenge):
        print("✅ Event_Titan-Challenge_Button gedrückt!")
        time.sleep(3)

    for i in range(2):
        print(f"🔄 Runde {i+1}/2")

        # 52. Titan-Challenge_Challenge_Button drücken
        if click_button(button_TitanChallengeChallenge):
            print("✅ Titan-Challenge_Challenge_Button gedrückt!")
            time.sleep(14)

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

        # 58. Angriff_Bestatigen_Button drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 59. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(75) # Warten bis der Angriff zuende ist

        # 60. button_Angriff_Belohnung drücken
        if click_button(button_Angriff_Belohnung):
            print("✅ Angriff_Belohnung_Button gedrückt!")
            time.sleep(6)

    
    # 61. Zurück_Button drücken
    if click_button(button_Zuruck):
        time.sleep(2)
        print("✅ Zurück_Button gedrückt!")

        




    #HIER NOCH MIT DER ANDEREN SCREENSHOT FUNKTION AUSPROBIEREN (Sammelzentrum_nichtfindbare buttons testen und sie finden lassen.py)!!!!!!!!!!!!!!!!!!!
    #SAMMELZENTRUM machen
    # 62. Sammelzentrum_Button drücken
    '''if click_button(button_Sammelzentrum):
        print("✅ Sammelzentrum_Button gedrückt!")
        time.sleep(2)

    #einmal clicken falls ich Belhonungen einsammeln muss
    mauszeiger_mittig()
    pyautogui.click()
    time.sleep(2)

    # Flag, um zu prüfen, ob die Koordinaten schon gespeichert wurden für die while schleife
    coordinates_saved = False
    coord1, coord2 = None, None

    while True:
        # Überprüfen, ob Sammelzentrum-Buttons gefunden wurden
        screenshot_path = take_screenshot()
        button_positions = find_buttons(screenshot_path, button_Sammelzentrum_templates)

        if not button_positions:
            print("❌ Keine Sammelzentrum-Buttons gefunden. Schleife wird beendet.")
            break

        # 64. Sammelzentrum_Buttons suchen und klicken (Funktioniert noch nicht ganz)
        click_sammelzentrum_buttons(x, y, width, height)
        time.sleep(1)

        # 65. Sammelzentrum_Transport_Button drücken
        if click_button(button_Sammelzentrum_Transport):
            print("✅ Sammelzentrum_Transport_Button gedrückt!")
            time.sleep(2)

        # 67. Auf die Koordinaten klicken von den 2 Flugzeugen
        if not coordinates_saved:
            coord1, coord2 = find_and_save_coordinates(find_cords1, find_cords2)
            if coord1 and coord2:
                coordinates_saved = True
        click_at_coordinates(coord1, coord2)

        # 66. Sammelzentrum_Bestatigen_Button drücken
        if click_button(button_Sammelzentrum_Bestatigen):
            print("✅ Sammelzentrum_Bestatigen_Button gedrückt!")
            time.sleep(2)

    #einmal clicken falls ich Belhonungen einsammeln muss
    pyautogui.click()
    time.sleep(2)

    # Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)'''




    #ENDLOSES ABENTEUER machen
    # 65. EndlosesAbenteuer_Button drücken
    if click_button(button_EndlosesAbenteuer):
        print("✅ EndlosesAbenteuer_Button gedrückt!")
        time.sleep(2)
    
    # 65. EndlosesAbenteuer_Verbleibend_Button drücken
    if click_button(button_EndlosesAbenteuer_Verbleibend):
        print("✅ EndlosesAbenteuer_Verbleibend_Button gedrückt!")
        time.sleep(2)

    # 65. EndlosesAbenteuer_Skip_Button drücken
    if click_button(button_EndlosesAbenteuer_Skip):
        print("✅ EndlosesAbenteuer_Skip_Button gedrückt!")
        time.sleep(2)

    # 65. EndlosesAbenteuer_Bestatigen_Buttonn drücken
    if click_button(button_EndlosesAbenteuer_Bestatigen):
        print("✅ EndlosesAbenteuer_Bestatigen_Button gedrückt!")
        time.sleep(14)

    # 65. Angriff_Bestatigen_Buttonn drücken
    if click_button(button_Angriff_Bestatigen):
        print("✅ Angriff_Bestatigen_Button gedrückt!")
        time.sleep(2)

    # 65. Angriff_Starten_Button drücken
    if click_button(button_Angriff_Starten):
        print("✅ Angriff_Starten_Button gedrückt!")
        time.sleep(2)

    # 1. while-Schleife läuft unendlich, bis sie mit break gestoppt wird
    while True:
        if not click_button(button_Schliessen):
            print("❌ Schliessen_Button nicht mehr gefunden! Breche die Schleife ab.")
            break
        
        # 2. while-Schleife: Button wird wiederholt gedrückt, solange er gefunden wird
        while click_button(button_Schliessen):
            time.sleep(2)
            print("✅ Schliessen_Button wurde wiederholt gedrückt!")

        time.sleep(120)  # Wartezeit nach dem Drücken
        screenshot_path = take_screenshot()

    # 65. Angriff_Bestätigen_Button drücken Um Behlonung einzusammeln
    if click_button(button_Angriff_Bestatigen):
        print("✅ Angriff_Bestätigen_Button gedrückt!")
        time.sleep(2)

    # Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #HERAUSFORDERUNG machen
    # 66. Herausforderung_Button drücken
    if click_button(button_Herausforderung):
        print("✅ Herausforderung_Button gedrückt!")
        time.sleep(2)

    # Schleife, die 5 Mal durchläuft
    for i in range(5):
        print(f"🔄 Runde {i+1}/5")

        time.sleep(9)

        # 66. Herausforderung_Starten_Button drücken
        if click_button(button_Herausforderung_Starten):
            print("✅ Herausforderung_Starten_Button gedrückt!")
            time.sleep(25)

        # 67. Angriff_Hauptkanone_Button drücken
        if click_button(button_Angriff_Hauptkanone):
            print("✅ Angriff_Hauptkanone_Button gedrückt!")
            time.sleep(2)

        # 68. Angriff_Hauptkanone_Upgrade_Button drücken
        if click_button(button_Angriff_Hauptkanone_Upgrade):
            print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 69. Angriff_Rakete_Button drücken
        if click_button(button_Angriff_Rakete):
            print("✅ Angriff_Rakete_Button gedrückt!")
            time.sleep(2)

        # 70. Angriff_Rakete_Upgrade_Button drücken
        if click_button(button_Angriff_Rakete_Upgrade):
            print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Nebenkanone_Button drücken
        if click_button(button_Angriff_Nebenkanone):
            print("✅ Angriff_Nebenkanone_Button gedrückt!")
            time.sleep(2)

        # 72. Angriff_Bestatigen_Button als vorletzter Schritt
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 74. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(55) # Warten bis der Angriff zu Ende ist

        # 75. Abschluss: Angriff_Bestatigen_Button noch einmal drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button (Abschluss) gedrückt!")
            time.sleep(9)

    # Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    mauszeiger_mittig()
    scroll_down()
    time.sleep(2)




    #ENTSENDUNG machen
    # 66. Entsendung_Button drücken
    if click_button(button_Entsendung):
        print("✅ Entsendung_Button gedrückt!")
        time.sleep(2)
    
    # 67. Abholen button 5 mal drücken + 4 mal belohnung abholen
    if click_top_button(button_EntsendungAbholen, clicks=10):
        print("✅ EntsendungAbholen_Button 5-mal gedrückt!")

    # 49. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        scroll_up()
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #LEGIONEVENT
    # 66. Legion_Button drücken
    if click_button(button_Legion):
            print("✅ Legion_Button gedrückt!")
            time.sleep(2)

    # 66. Legion_Event_Button drücken
    if click_button(button_Legion_Event):
            print("✅ Legion_Event_Button gedrückt!")
            time.sleep(2)

    # 66. Legion_Event_Legionsjagd_Button drücken
    if click_button(button_Legion_Event_Legionsjagd):
            print("✅ Legion_Event_Legionsjagd_Button gedrückt!")
            time.sleep(2)

    # Die 3 Legion Event Angriffe machen
    for i in range(3):
        print(f"🔄 Runde {i+1}/3")

        time.sleep(9)

        # 66. Legion_Event_Challenge_Button drücken
        if click_button(button_Legion_Event_Challenge):
                print("✅ Legion_Event_Challenge_Button gedrückt!")
                time.sleep(25)

        # 67. Angriff_Hauptkanone_Button drücken
        if click_button(button_Angriff_Hauptkanone):
            print("✅ Angriff_Hauptkanone_Button gedrückt!")
            time.sleep(2)

        # 68. Angriff_Hauptkanone_Upgrade_Button drücken
        if click_button(button_Angriff_Hauptkanone_Upgrade):
            print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 69. Angriff_Rakete_Button drücken
        if click_button(button_Angriff_Rakete):
            print("✅ Angriff_Rakete_Button gedrückt!")
            time.sleep(2)

        # 70. Angriff_Rakete_Upgrade_Button drücken
        if click_button(button_Angriff_Rakete_Upgrade):
            print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Nebenkanone_Button drücken
        if click_button(button_Angriff_Nebenkanone):
            print("✅ Angriff_Nebenkanone_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Bestatigen_Button drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(60) # warten bis der Angriff beendet ist

        # 71. Legion_Angriff_Zuruck_Button drücken
        if click_button(button_Legion_Angriff_Zuruck):
            print("✅ Legion_Angriff_Zuruck_Button gedrückt!")
            time.sleep(2)

    time.sleep(8)

    # 66. Zurück_Button 2 mal drücken
    for i in range(2):
        if click_button(button_Zuruck):
            print("✅ Zurück_Button gedrückt!")
            time.sleep(2)
    
    # 71. Home_Button drücken
    if click_button(button_Home):
        print("✅ Home_Button gedrückt!")
        time.sleep(2)
    



    #UNICOEVENT machen
    # Cybertron_Held_Button drücken
    if click_button(button_Cybertron_Held):
        print("✅ Cybertron_Held_Button gedrückt!")
        time.sleep(2)

    # StarCave_Voyage_Button drücken
    if click_button(button_StarCave_Voyage):
        print("✅ StarCave_Voyage_Button gedrückt!")
        time.sleep(2)

    # StarCave_Abholen_Button drücken
    if click_button(button_StarCave_Abholen):
        print("✅ StarCave_Abholen_Button gedrückt!")
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)

    # Unico_Zurück_Button drücken
    if click_button(button_Unico_Zuruck):
        print("✅ Unico_Zurück_Button gedrückt!")
        time.sleep(2)

    # UnicoResist_Unicorn_Button drücken
    if click_button(button_UnicoResist_Unicorn):
        print("✅ UnicoResist_Unicorn_Button gedrückt!")
        time.sleep(2)

    # Die 2 Unico Event Angriffe machen
    for i in range(2):
        print(f"🔄 Runde {i+1}/2")

        time.sleep(9)

        # 66. Unico_Chllenge_Button drücken
        if click_button(button_Unico_Chllenge):
                print("✅ Unico_Chllenge_Button gedrückt!")
                time.sleep(25)

        # 67. Angriff_Hauptkanone_Button drücken
        if click_button(button_Angriff_Hauptkanone):
            print("✅ Angriff_Hauptkanone_Button gedrückt!")
            time.sleep(2)

        # 68. Angriff_Hauptkanone_Upgrade_Button drücken
        if click_button(button_Angriff_Hauptkanone_Upgrade):
            print("✅ Angriff_Hauptkanone_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 69. Angriff_Rakete_Button drücken
        if click_button(button_Angriff_Rakete):
            print("✅ Angriff_Rakete_Button gedrückt!")
            time.sleep(2)

        # 70. Angriff_Rakete_Upgrade_Button drücken
        if click_button(button_Angriff_Rakete_Upgrade):
            print("✅ Angriff_Rakete_Upgrade_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Nebenkanone_Button drücken
        if click_button(button_Angriff_Nebenkanone):
            print("✅ Angriff_Nebenkanone_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Bestatigen_Button drücken
        if click_button(button_Angriff_Bestatigen):
            print("✅ Angriff_Bestatigen_Button gedrückt!")
            time.sleep(2)

        # 71. Angriff_Starten_Button drücken
        if click_button(button_Angriff_Starten):
            print("✅ Angriff_Starten_Button gedrückt!")
            time.sleep(60) # warten bis der Angriff beendet ist

        # 71. Unico_Angriff_Zuruck_Button drücken
        if click_button(button_Legion_Angriff_Zuruck):
            print("✅ Unico_Angriff_Zurück_Button gedrückt!")
            time.sleep(9)

    time.sleep(9)

    # 66. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 66. Unico_Schiessubung-Button drücken
    if click_button(button_Unico_Schiessubung):
        print("✅ Unico_Schiessubung_Button gedrückt!")
        time.sleep(2)

    # Unico 3 mal die Schiessübung machen
    for i in range(3):
        print(f"🔄 Runde {i+1}/3")

        time.sleep(9)

        # 66. Unico_Schiessubung_Starten_Button drücken
        if click_button(button_Unico_Schiessubung_Starten):
            print("✅ Unico_Schiessubung_Starten_Button gedrückt!")
            time.sleep(2)

        # 66. Unico_Schiessubung_Starten_Starten_Button drücken
        if click_button(button_Unico_Schiessubung_Starten_Starten):
            print("✅ Unico_Schiessubung_Starten_Starten_Button gedrückt!")
            time.sleep(2)

        # Warten bis die Schiessübung zuende ist    
        time.sleep(10)

        # 66. Unico_Schiessubung_Bestatigen_Button drücken
        if click_button(button_Unico_Schiessubung_Bestatigen):
            print("✅ Unico_Schiessubung_Bestatigen_Button gedrückt!")
            time.sleep(2)

    # 66. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # StarCave_Voyage_Button drücken
    if click_button(button_StarCave_Voyage):
        print("✅ StarCave_Voyage_Button gedrückt!")
        time.sleep(2)

    # StarCave_Abholen_Button drücken
    if click_button(button_StarCave_Abholen):
        print("✅ StarCave_Abholen_Button gedrückt!")
        time.sleep(2)
        pyautogui.click()
        time.sleep(2)

    # Unico_Zurück_Button drücken
    if click_button(button_Unico_Zuruck):
        print("✅ Unico_Zurück_Button gedrückt!")
        time.sleep(2)
        
    # 66. Unico_Event_Aufgaben_Button drücken
    if click_button(button_Unico_Event_Aufgaben):
        print("✅ Unico_Event_Aufgaben_Button gedrückt!")
        time.sleep(2)

    # 66. Unico_Event_Aufgaben_Abholen_Button drücken
    if click_button(button_Unico_Event_Aufgaben_Abholen):
        print("✅ Unico_Event_Aufgaben_Abholen_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        pyautogui.click()
        time.sleep(2)
    
    # 66. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 66. Zurück2_Button drücken um zum Home zu kommen
    if click_button(button_Unico_Zuruck2):
        print("✅ Zurück2_Button gedrückt!")
        time.sleep(2)




    #ENERGIE AUFLADEN
    time.sleep(30152) #hier warten bis ich wieder genug energie habe (50)
    #Prüfen ob Schliessen Button da sind und ob Start Zurück Button da sind
    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_StartZuruck):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)




    #STARKE-FEINDHERAUSFORDERUNG machen
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

    # 21. Starke-Feindherausforderung_Grad1_Button klicken
    if click_button(button_StarkeFeindherausforderungGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 25. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #NACHSCHUB machen
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

    # 48. Schließen_Button noch 1 Mal
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 45. Nachschub_Grad1_Button klicken
    if click_button(button_NachschubGrad1):
        print("✅ Nachschub_Grad1_Button gedrückt!")
        time.sleep(2)

    # 49. Zurück_Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        scroll_down()
        time.sleep(2)




    #VERLORENES-SCHLACHTFELD machen
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

    # 27. Verlorenes-Schlachtfeld_Grade1_Button klicken
    if click_button(button_VerlorenesSchlachtfeldGrad1):
        print("✅ Verlorenes-Schlachtfeld_Grade1_Button gedrückt!")
        time.sleep(2)

    # 43. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
    



    #ENDECKE-DAS-WOLKENMEER machen
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

    # 33. Entdecke-das-Wolkenmeer_Grade1_Button klicken
    if click_button(button_EntdeckedasWolkenmeerGrad1):
        print("✅ Entdecke-das-Wolkenmeer_Grade1_Button gedrückt!")
        time.sleep(2)

    # 37. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)




    #TÖDLICHER ANGRIFF machen
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

    # 39. Todlicher-Angriff_Grade1_Button klicken
    if click_button(button_TödlicherAngriffGrad1):
        print("✅ Todlicher-Angriff_Grade1_Button gedrückt!")
        time.sleep(2)

    # 37. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)
        mauszeiger_mittig()
        scroll_up()
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)



    time.sleep(3020) #hier warten bis ich wieder genug energie habe (5)
    #Prüfen ob Schliessen Button da sind und ob Start Zurück Button da sind
    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_Schliessen):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 65. Schliessen_Button drücken
    if click_button(button_StartZuruck):
        print("✅ Schliessen_Button gedrückt!")
        time.sleep(2)

    # 7. Tagesevent_Button klicken
    if click_button(button_Tagesevent):
        print("✅ Tagesevent_Button gedrückt!")
        time.sleep(2)
    


    
    #BOMBARDIERUNG machen
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

    # 17. Abbrechen_Button klicken
    if click_button(button_Tagesevent_Abbrechen):
        print("✅ Abbrechen_Button gedrückt!")
        time.sleep(2)

    # 18. Schließen-Button klicken
    if click_button(button_Schliessen):
        print("✅ Start_Schliessen_Button nochmal gedrückt!")
        time.sleep(2)

    # 15. Bombardierung_Grad1_Button klicken
    if click_button(button_BombardierungGrad1):
        print("✅ Luftseesimulation_Grad1_Button gedrückt!")
        time.sleep(2)

    # 19. Zurück-Button drücken
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)

    # 49. Zurück_Button drücken um zum Home zu kommen
    if click_button(button_Zuruck):
        print("✅ Zurück_Button gedrückt!")
        time.sleep(2)