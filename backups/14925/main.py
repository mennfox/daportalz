import os
import json


# Clear screen based on OS
os.system('cls' if os.name == 'nt' else 'clear')



def main_menu():
    while True:
        print("\n🌿 Grow Dashboard Interface")
        print("1. Add New Plants")
        print("2. Update Repot Dates")
        print("3. Log Height")
        print("4. Watering Log")
        print("5. View Grow Tracker")
        print("6. Start New Grow (Archive + Reset)")
        print("7. View Archived Grow Summaries") 
        print("8. Harvest Stats")
        print("9. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            os.system("python3 grow.py")
        elif choice == "2":
            os.system("python3 repot.py")
        elif choice == "3":
            os.system("python3 modules/height.py")
        elif choice == "4":
            os.system("python3 watering_log.py")
        elif choice == "5":
            os.system("python3 test.py")
        elif choice == "6":
            confirm = input("⚠️ This will archive and delete your current grow data. Are you sure? (y/n): ").strip().lower()
            if confirm == "y":
                try:
                    from modules.height import load_plants, archive_grow, append_readable_archive
                    plants = load_plants()
                    if plants:
                        archive_grow(plants)
                        append_readable_archive(plants)
                    os.remove("/home/pi/plants.json")
                    print("🧹 Grow data archived and reset.")
                except Exception as e:
                    print(f"❌ Error during archive/reset: {e}")
                else:
                    print("🚫 Cancelled. No changes made.")
        elif choice == "7":
            archive_path = "/home/pi/grow_archive/grow_archive.txt"
            if os.path.exists(archive_path):
                os.system(f"micro {archive_path}")
            else:
                print("📁 No archive file found yet.")
        elif choice == "8":
            try:
                with open("/home/pi/plants.json", "r") as f:
                    plants = json.load(f)
                for plant in plants:
                    name = plant.get("name", "Unnamed")
                    current = plant.get("harvest_weight", None)
                    print(f"\n🌿 {name}")
                    print(f"Current harvest: {current if current else '[None]'}")
                    new_weight = input("Enter harvest weight (g) or leave blank: ").strip()
                    if new_weight:
                        try:
                            plant["harvest_weight"] = float(new_weight)
                        except ValueError:
                            print("❌ Invalid number. Skipping.")
                with open("plants.json", "w") as f:
                    json.dump(plants, f, indent=2)
                print("✅ Harvest weights updated.")
            except Exception as e:
                print(f"❌ Error updating harvest stats: {e}")
        
        elif choice == "9":
            print("👋 Exiting dashboard.")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()

