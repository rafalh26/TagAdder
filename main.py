import re

# Bible book lists
chapterListOld = []
chaptersListOldDeuterocanonical = []
chaptersListNew = []
coding = ""


def SetParameters():
    global chapterListOld, coding, chaptersListOldDeuterocanonical, chaptersListNew

    coding = 'utf-8'

    chapterListOld = [
        "Księga Rodzaju", "Księga Wyjścia", "Księga Kapłańska", "Księga Liczb", "Księga Powtórzonego Prawa",
        "Księga Jozuego", "Księga Sędziów", "Księga Rut", "1 Księga Samuela", "2 Księga Samuela",
        "1 Księga Królewska", "2 Księga Królewska", "1 Księga Kronik", "2 Księga Kronik",
        "Księga Ezdrasza", "Księga Nehemiasza", "Księga Estery", "Księga Hioba", "Księga Psalmów",
        "Księga Przysłów", "Księga Koheleta", "Pieśń nad Pieśniami", "Księga Izajasza",
        "Księga Jeremiasza", "Lamentacje Jeremiasza", "Księga Ezechiela", "Księga Daniela",
        "Księga Ozeasza", "Księga Joela", "Księga Amosa", "Księga Abdiasza", "Księga Jonasza",
        "Księga Micheasza", "Księga Nahuma", "Księga Habakuka", "Księga Sofoniasza",
        "Księga Aggeusza", "Księga Zachariasza", "Księga Malachiasza"
    ]
    chaptersListOldDeuterocanonical = [
        "Księga Tobiasza", "Księga Judyty", "1 Księga Machabejska", "2 Księga Machabejska",
        "Księga Mądrości", "Mądrość Syracha", "Księga Barucha"
    ]
    chaptersListNew = [
        "Ewangelia Mateusza", "Ewangelia Marka", "Ewangelia Łukasza", "Ewangelia Jana",
        "Dzieje Apostolskie", "List do Rzymian", "1 List do Koryntian", "2 List do Koryntian",
        "List do Galatów", "List do Efezjan", "List do Filipian", "List do Kolosan",
        "1 List do Tesaloniczan", "2 List do Tesaloniczan", "1 List do Tymoteusza", "2 List do Tymoteusza",
        "List do Tytusa", "List do Filemona", "List do Hebrajczyków", "List św. Jakuba",
        "1 List św. Piotra", "2 List św. Piotra", "1 List św. Jana", "2 List św. Jana",
        "3 List św. Jana", "List św. Judy", "Apokalipsa św. Jana"
    ]


def format_bible_text(text):
    # Combine all book names
    all_books = chapterListOld + chaptersListOldDeuterocanonical + chaptersListNew

    # First, remove ALL newlines to ensure verses stay together
    text = re.sub(r'\r\n', ' ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r' +', ' ', text)

    # Process book names - ensure each is on its own line
    for book in all_books:
        text = re.sub(rf"\s*({re.escape(book)})\s*", r"\n\1\n", text, flags=re.IGNORECASE)

    # Special handling for Psalms
    text = re.sub(r'\s*Psalm\s+(\d+)\s*', r'\nPsalm \1\n', text, flags=re.IGNORECASE)
    # Process other chapters
    text = re.sub(r'\s*Rozdział\s+(\d+)\s*', r'\nRozdział \1\n', text, flags=re.IGNORECASE)

    # Now process verses
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    output = []
    current_book = ""

    for line in lines:
        # Check if it's a book title
        if any(book.lower() == line.lower() for book in all_books):
            current_book = line
            output.append(line)
            continue

        # Check if it's a chapter heading
        if current_book.lower() == "księga psalmów":
            psalm_match = re.match(r'^Psalm (\d+)$', line, re.IGNORECASE)
            if psalm_match:
                output.append(f"Psalm {psalm_match.group(1)}")
                continue
        else:
            chapter_match = re.match(r'^Rozdział (\d+)$', line, re.IGNORECASE)
            if chapter_match:
                output.append(f"Rozdział {chapter_match.group(1)}")
                continue

        # Process verse lines - split into individual verses
        verses = re.findall(r'(\d+) ([^\d]+)(?=\d+|$)', line + ' ')

        for verse_num, verse_text in verses:
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            output.append(f"{verse_num} {clean_text}")

    # Final cleanup
    formatted_text = '\n'.join(output)
    formatted_text = re.sub(r'\n\n+', '\n', formatted_text).strip()

    return formatted_text


def tag_bible_text(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]

    output = []
    current_book = ""
    current_chapter = ""
    chapter_opened = False  # Track if we have an open chapter tag

    for line in lines:
        # Check if it's a book title
        book_match = None
        for book in chapterListOld + chaptersListOldDeuterocanonical + chaptersListNew:
            if line.lower() == book.lower():
                book_match = book
                break

        if book_match:
            # Close previous book if exists (properly handling chapters)
            if current_book:
                if chapter_opened:
                    output.append("</c>")
                    chapter_opened = False
                output.append("</b>")

            current_book = book_match
            output.append(f'<b n="{current_book}">')
            current_chapter = ""
            continue

        # Check if it's a chapter heading
        if current_book.lower() == "księga psalmów":
            psalm_match = re.match(r'^Psalm (\d+)$', line, re.IGNORECASE)
            if psalm_match:
                if chapter_opened:
                    output.append("</c>")
                current_chapter = psalm_match.group(1)
                output.append(f'<c n="{current_chapter}">')
                chapter_opened = True
                continue
        else:
            chapter_match = re.match(r'^Rozdział (\d+)$', line)
            if chapter_match:
                if chapter_opened:
                    output.append("</c>")
                current_chapter = chapter_match.group(1)
                output.append(f'<c n="{current_chapter}">')
                chapter_opened = True
                continue

        # Process verses
        verse_match = re.match(r'^(\d+) (.+)$', line)
        if verse_match:
            # If we encounter a verse without chapter, start chapter 1
            if not chapter_opened:
                current_chapter = "1"
                output.append(f'<c n="{current_chapter}">')
                chapter_opened = True

            verse_num = verse_match.group(1)
            verse_text = verse_match.group(2)
            output.append(f'<v n="{verse_num}">{verse_text}</v>')

    # Close final tags properly
    if chapter_opened:
        output.append("</c>")
    if current_book:
        output.append("</b>")

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(output))


def main():
    SetParameters()
    print("Bible Text Processor")
    print("====================")
    print("1. Format only (input.txt → output.txt)")
    print("2. Tag only (output.txt → PROCESSED.txt)")
    print("3. Full processing (input.txt → output.txt → PROCESSED.txt)")
    print("4. Exit")

    while True:
        choice = input("\nSelect operation (1-4): ").strip()

        if choice == "1":
            try:
                with open("input.txt", "r", encoding="utf-8") as file:
                    input_text = file.read()
                formatted_text = format_bible_text(input_text)
                with open("output.txt", "w", encoding="utf-8") as file:
                    file.write(formatted_text)
                print("\nFormatting complete. Results saved to output.txt")
            except FileNotFoundError:
                print("\nError: input.txt not found")
            break

        elif choice == "2":
            try:
                tag_bible_text("output.txt", "PROCESSED.txt")
                print("\nTagging complete. Results saved to PROCESSED.txt")
            except FileNotFoundError:
                print("\nError: output.txt not found. Please run format operation first.")
            break

        elif choice == "3":
            try:
                # Formatting step
                with open("input.txt", "r", encoding="utf-8") as file:
                    input_text = file.read()
                formatted_text = format_bible_text(input_text)
                with open("output.txt", "w", encoding="utf-8") as file:
                    file.write(formatted_text)

                # Tagging step
                tag_bible_text("output.txt", "PROCESSED.txt")
                print("\nFull processing complete. Results saved to:")
                print("- output.txt (formatted text)")
                print("- PROCESSED.txt (tagged XML)")
            except FileNotFoundError as e:
                print(f"\nError: {e.filename} not found")
            break

        elif choice == "4":
            print("\nExiting...")
            break

        else:
            print("\nInvalid choice. Please enter 1-4")


if __name__ == "__main__":
    main()