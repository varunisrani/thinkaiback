#!/usr/bin/env python3
"""
Create a comprehensive sample script to test the ADK agent properly
Since the Black Panther PDF is corrupted, we'll create a proper multi-page script
"""

def create_comprehensive_script():
    """Create a realistic 10-page script for testing."""
    
    script_content = """
=== PAGE 1 ===
FADE IN:

EXT. WAKANDA BORDER - FOREST - DAY

The lush African landscape stretches endlessly. BORDER TRIBE WARRIORS patrol the perimeter, their vibranium spears gleaming in the sunlight.

WARRIOR 1 (into comm)
Sector Seven clear. No movement detected.

A rustling in the bushes. The warriors tense, weapons ready.

ERIK KILLMONGER emerges from the shadows, hands raised.

KILLMONGER
I'm here to challenge for the throne.

=== PAGE 2 ===
INT. WAKANDA PALACE - THRONE ROOM - DAY

T'CHALLA sits regally on the panther throne, the Black Panther suit gleaming. OKOYE and the DORA MILAJE stand guard.

OKOYE
My king, there's been an intrusion at the border.

T'CHALLA
What kind of intrusion?

OKOYE
Someone claiming royal blood. Demanding a challenge.

T'CHALLA rises, concern etched on his face.

T'CHALLA
Bring them to me.

=== PAGE 3 ===
INT. WAKANDA PALACE - LABORATORY - DAY

SHURI works frantically on new Black Panther technology. Holographic displays show vibranium analysis and suit upgrades.

SHURI
(to herself)
If I can increase the kinetic absorption by fifteen percent...

She tests a new gauntlet on a training dummy. BLAST! The dummy disintegrates.

SHURI
(grinning)
Brother's going to love this.

RAMONDA enters, worried.

RAMONDA
Shuri, your brother needs you in the throne room.

=== PAGE 4 ===
EXT. WARRIOR FALLS - DAY

The sacred waterfall thunders down ancient cliffs. Tribal elders gather in ceremonial dress. T'CHALLA and KILLMONGER face each other on the fighting platform.

ZURI
(chanting)
Ancient combat for the crown. Victory by yield or death.

KILLMONGER
(stripping off shirt, revealing ritual scars)
I've been waiting for this my whole life.

T'CHALLA
This doesn't have to end in blood.

KILLMONGER
Blood built this nation. Blood will rebuild it.

They circle each other, muscles tensed for combat.

=== PAGE 5 ===
FIGHT SEQUENCE - WARRIOR FALLS

T'CHALLA lunges first, using his enhanced agility. Killmonger counters with brutal efficiency.

WHAM! Killmonger's fist connects with T'Challa's jaw.

T'CHALLA flips backward, landing gracefully. He sweeps Killmonger's legs.

KILLMONGER
(rolling to safety)
Nice moves, cousin.

The fight intensifies. Both warriors are evenly matched, trading devastating blows.

CRACK! T'Challa's ribs. He staggers.

=== PAGE 6 ===
INT. ANCESTRAL PLANE - CONTINUOUS

T'CHALLA finds himself in the purple-tinged spirit realm. Ancient baobab trees stretch toward infinity.

T'CHAKA appears, ethereal and wise.

T'CHAKA
My son. You are in great danger.

T'CHALLA
Baba, I don't understand. Who is this man?

T'CHAKA
(heavy with regret)
Your cousin. My nephew. I failed him.

T'CHALLA
What do you mean?

T'CHAKA
I left him behind. In Oakland. With his father's body.

=== PAGE 7 ===
EXT. WARRIOR FALLS - CONTINUOUS

Back in the real world, Killmonger has the upper hand. T'Challa lies bloodied on the rocky platform.

KILLMONGER
(standing over him)
I ain't nothing like you. You're nothing but another scared little boy.

He raises his spear for the killing blow.

KILLMONGER
Wakanda forever!

SPEAR THRUST! T'Challa falls into the churning waters below.

The crowd gasps. Shuri screams.

KILLMONGER
(to the crowd)
Your king is dead! I am T'Challa!

=== PAGE 8 ===
INT. WAKANDA PALACE - THRONE ROOM - NIGHT

Killmonger sits on the panther throne, now wearing royal garb. The Dora Milaje stand uneasily at attention.

KILLMONGER
Burn all the heart-shaped herbs. Except one.

SHURI
You cannot destroy our legacy!

KILLMONGER
Your legacy is built on lies and isolation.

W'KABI enters with BORDER TRIBE WARRIORS.

W'KABI
My king, what are your orders?

KILLMONGER
Prepare for war. The sun has set on Wakanda's isolation.

=== PAGE 9 ===
EXT. MOUNT BASHENGA - NIGHT

Deep in the sacred mountain, M'BAKU and his JABARI WARRIORS have rescued T'Challa from the frozen waters.

M'BAKU
Your king lives, but barely.

NAKIA
Can you save him?

M'BAKU
The heart-shaped herb could heal him, but...

SHURI
(producing a single herb)
I saved one before they burned the garden.

She prepares the ceremonial drink. T'Challa's life hangs in the balance.

RAMONDA
(praying)
Please, ancestors, don't take my son.

=== PAGE 10 ===
INT. ANCESTRAL PLANE - CONTINUOUS

T'Challa walks with his father through the spirit realm.

T'CHAKA
You must return, my son. Wakanda needs you.

T'CHALLA
I failed them. I failed you.

T'CHAKA
A king who fails to learn from his mistakes is no king at all.

T'CHALLA
What should I do?

T'CHAKA
Your duty. But also your heart. Wakanda must evolve.

T'Challa nods, understanding flooding his eyes.

T'CHALLA
I will not abandon the world as you did.

FADE TO BLACK.

=== END OF SAMPLE SCRIPT ===
"""
    
    return script_content.strip()

def save_sample_script():
    """Save the sample script to a file."""
    script = create_comprehensive_script()
    
    # Save as text file
    with open("/Users/varunisrani/Desktop/mckays-app-template 3/sd1/SAMPLE_SCRIPT_10_PAGES.txt", "w") as f:
        f.write(script)
    
    print("✅ Created SAMPLE_SCRIPT_10_PAGES.txt")
    
    # Calculate statistics
    pages = script.count("=== PAGE")
    scenes_with_int_ext = script.count("INT.") + script.count("EXT.")
    total_chars = len(script)
    total_words = len(script.split())
    
    print(f"📊 Script Statistics:")
    print(f"   Pages: {pages}")
    print(f"   INT/EXT scenes: {scenes_with_int_ext}")
    print(f"   Total characters: {total_chars}")
    print(f"   Total words: {total_words}")
    print(f"   Estimated script length: {total_words / 250:.1f} pages (industry standard)")
    
    return script

if __name__ == "__main__":
    save_sample_script()