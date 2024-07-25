import logging
from collections import Counter
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
import datetime
import re
import requests
from bs4 import BeautifulSoup

# Download WordNet data
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')

# Configure logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#Get text from website
def get_text_from_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        logging.error("Failed to retrieve text from the website.")
        return None

def parse_html(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def find_elements(soup, book, chapter):
    class_content = []
    verse_number = 1

    while True:
        # Construct the class name dynamically
        class_name = f"text {book}-{chapter}-{verse_number}"

        # Find all elements with the constructed class name
        elements = soup.find_all(class_=class_name)

        if not elements:  # If no elements found, exit the loop
            break

        class_content.extend(elements)
        verse_number += 1
    return class_content

def extract_text(class_content):
    if class_content:
        # Extract text from found elements
        text_elements = [content.text.strip() for content in class_content]
        # Combine text from all verses into one big text
        combined_text = '\n'.join(text_elements)
        combined_text = re.sub(r'\([A-Z]+\)', '', combined_text)
        # Remove brackets with any content
        combined_text = re.sub(r'\[.*?\]', '', combined_text)
        return text_elements, combined_text
    else:
        return "Class not found", None

def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts."""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

def find_words_in_text(text_content, words_to_find):
    #Initialize Lemmatizer
    lemmatizer = WordNetLemmatizer()
    found_words = []
    found_lines = {}
    lemmatized_words_to_find = {lemmatizer.lemmatize(word.lower()) for word in words_to_find}

    # Split text into lines and track chapter
    lines = text_content.split('\n')
    chapter = 0
    for line_number, line in enumerate(lines, start=1):
        if line.startswith('Chapter '):
            chapter = int(re.search(r'\d+', line).group())
        else:
            words = line.split()
            lemmatized_words = [lemmatizer.lemmatize(word.lower()) for word in words]
            if any(lemmatized_word in lemmatized_words_to_find for lemmatized_word in lemmatized_words):
                found_lines[(chapter, line_number)] = line
                for word_position, word in enumerate(words, start=1):
                    lemmatized_word = lemmatizer.lemmatize(word.lower())
                    if lemmatized_word in lemmatized_words_to_find:
                        found_words.append((word, chapter, line_number, word_position)) # Store word, chapter, line number, and word position

    return found_words, found_lines

def most_common_words_in_text(text_content):
    # Initialize an empty Counter to store word counts
    word_counts = Counter()

    # Define common words to exclude
    common_words = [
        "of", "my", "me", "on", "it", "not", "as", "who", "our", "have", "may", "people", "men", "she", "said", "will", "ord", "shall",
        "your", "to", "he", "his", "in", "was", "by", "a", "for", "is", "from", "when", "they", "you", "with", "that", "were", "then",
        "all","had","i","him","the","and","or","but","so","yet","because","although","since", "them", "there", "this", "be", "therefore",
        "however", "moreover", "furthermore", "nevertheless", "otherwise", "consequently", "hence", "thus", "meanwhile", "nonetheless", "likewise",
        "up", "out", "now", "at", "go", "their", "did", "before", "her", "has", "down", "are", "us", "these", "no"
    ]

    # Convert common_words to lower case
    common_words = [word.lower() for word in common_words]

    # Remove punctuation and convert text to lowercase
    cleaned_text = re.sub(r'[^?\w\s]', '', text_content.lower())

    # Split text into words
    words = cleaned_text.split()

    #Initialize Lemmatizer
    lemmatizer = WordNetLemmatizer()

    # Lemmatize words and exclude common words
    words = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in words if word not in common_words]

    # Update the word counts
    #word_counts = Counter(words)
    word_counts.update(words)

    # Get the 5 most common words
    most_common = word_counts.most_common(40)
    return most_common

# Introduction
print("\nMade by Mr. Bang, the one, but not only")
print("All scripture has been collected from https://www.biblegateway.com, on", datetime.date.today(), "\n")

# User Interface for choosing what bible version to use
bible_version = [
    "1: English Standard Version (ESV)",
    "2: King James Version (KJV)",
    "3: New International Version (NIV)"
]
bible_version_url = [
    "ESV",
    "KJV",
    "NIV"
]
for version in bible_version:
    print(version)

while True:
    try:
        selected_version = int(input("Write the number of the desired version: "))
        if 1 <= selected_version <= len(bible_version):
            break
    except ValueError:
        print("Please enter a valid number from the list.")

selected_version = selected_version - 1

# User Interface for choosing Old or New Testament
print("\nPlease choose which Testament")
while True:
    try:
        ot_nt_input = int(input("Old Testament is 1, New Testament is 2: ")) # Boolean where 1 is True and everything else is false
        if ot_nt_input in [1, 2]:
            ot_nt = ot_nt_input == 1  # Assign True if input is 1, False otherwise
            break
    except ValueError:
        print("Please enter either 1 or 2")

# User Interface for choosing what book
print("Nice, here is the list of books to choose from:")

# Choosing 1 makes and prints a list of the Old Testment books
if ot_nt == 1:
    old_testament = [
        "1: Genesis",
        "2: Exodus",
        "3: Leviticus",
        "4: Numbers",
        "5: Deuteronomy",
        "6: Joshua",
        "7: Judges",
        "8: Ruth",
        "9: I Samuel",
        "10: II Samuel",
        "11: I Kings",
        "12: II Kings",
        "13: I Chronicles",
        "14: II Chronicles",
        "15: Ezra",
        "16: Nehemiah",
        "17: Esther",
        "18: Job",
        "19: Psalms",
        "20: Proverbs",
        "21: Ecclesiates",
        "22: Song of Songs",
        "23: Isaiah",
        "24: Jeremiah",
        "25: Lamentations",
        "26: Ezekiel",
        "27: Daniel",
        "28: Hosea",
        "29: Joel",
        "30: Amos",
        "31: Obadiah",
        "32: Jonah",
        "33: Micah",
        "34: Nahum",
        "35: Habakkuk",
        "36: Zephaniah",
        "37: Haggai",
        "38: Zechariah",
        "39: Malachi",
    ]
    old_testament_url = [
        "Gen",
        "Exod",
        "Lev",
        "Num",
        "Deut",
        "Josh",
        "Judg",
        "Ruth",
        "1Sam",
        "2Sam",
        "1Kgs",
        "2Kgs",
        "1Chr",
        "2Chr",
        "Ezra",
        "Neh",
        "Esth",
        "Job",
        "Ps",
        "Prov",
        "Eccl",
        "Song",
        "Isa",
        "Jer",
        "Lam",
        "Ezek",
        "Dan",
        "Hos",
        "Joel",
        "Amos",
        "Obad",
        "Jonah",
        "Mic",
        "Nah",
        "Hab",
        "Zeph",
        "Hag",
        "Zech",
        "Mal",
    ]

# Choosing anything else makes and prints a list of the New Testament books
else:
    new_testament = [
        "1: Matthew",
        "2: Mark",
        "3: Luke",
        "4: John",
        "5: Acts",
        "6: Romans",
        "7: I Corinthians",
        "8: II Corinthians",
        "9: Galatians",
        "10: Ephesians",
        "11: Philippians",
        "12: Colossians",
        "13: I Thessalonians",
        "14: II Thessalonians",
        "15: I Timothy",
        "16: II Timothy",
        "17: Titus",
        "18: Philemon",
        "19: Hebrews",
        "20: James",
        "21: I Peter",
        "22: II Peter",
        "23: I John",
        "24: II John",
        "25: III John",
        "26: Jude",
        "27: Revelation",
    ]
    new_testament_url = [
        "Matt",
        "Mark",
        "Luke",
        "John",
        "Acts",
        "Rom",
        "1Cor",
        "2Cor",
        "Gal",
        "Eph",
        "Phil",
        "Col",
        "1Thess",
        "2Thess",
        "1Tim",
        "2Tim",
        "Titus",
        "Phlm",
        "Heb",
        "Jas",
        "1Pet",
        "2Pet",
        "1John",
        "2John",
        "3John",
        "Jude",
        "Rev",
    ]

active_testament = old_testament if ot_nt == 1 else new_testament
active_testament2 = old_testament_url if ot_nt == 1 else new_testament_url

for book in active_testament:
    print(book)

# Gets the relevant number from the list of books
while True:
    try:
        book_choice = int(input("Write the number of the book: "))
        if 1 <= book_choice <= len(active_testament):
            break
    except ValueError:
        print("Please enter a valid number from the list.")

# Choosing what file to open
file_index = book_choice - 1

# Website URL
base_url = 'https://www.biblegateway.com/passage/?search='
base_url_end = '&version='
# Define translation table to remove digits and colons
translation_table = str.maketrans("", "", "0123456789: ")
# Remove numbers and colons from each string in the list    
cleaned_list = [item.translate(translation_table) for item in active_testament]
specified_url = base_url + cleaned_list[file_index]
print(specified_url)
print("Collecting scripture, please wait...")

# The number of chapters in each book
book_chapter_number = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4] if ot_nt else [28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]
# Initialize an empty list to store HTML content for each chapter
html_contents = []
# How many times the program will get contents from a webpage
for chapter in range(book_chapter_number[file_index]):
    print (specified_url + "+" + str(chapter + 1))
    chapter_url = specified_url + "+" + str(chapter + 1) + base_url_end + bible_version_url[selected_version]
    chapter_html = get_text_from_website(chapter_url)
    if chapter_html:
        html_contents.append(chapter_html)

# Combine HTML contents of all chapters
html_content = ''.join(html_contents)

# Initialize empty lists for text content and combined text
text_contents = []
combined_texts = []
complete_text = ""
chapter_loop = 0
# Loop through each chapter to extract text and combine it
for chapter_html in html_contents:
    chapter_loop += 1
    soup = parse_html(chapter_html)
    class_content = find_elements(soup, active_testament2[file_index], chapter_loop)
    text_content, combined_text = extract_text(class_content)
    #text_contents.append(text_content)
    #combined_texts.append(combined_text)
    if combined_text:
        complete_text += f"Chapter {chapter_loop} \n{combined_text}\n\n{'-'*40}\n\n"

# Log and filter out None values from combined_texts
for i, text in enumerate(combined_texts):
    if text is None:
        logging.warning(f"None found at index {i}")

combined_text = '\n'.join(combined_texts)

while True:
    while True:
        # User Interface for choosing program
        print("Choose a mode:", "1 = Find word,", "2 = Find repeated words")
        try:
            choice = int(input("Make your choice: "))
            if choice in [1, 2]:
                break
        except ValueError:
            print("Please enter either 1 or 2")

    # Find word in book
    if choice == 1:
        print("\nWhat words do you wish to find?")
        words_to_find = input().lower().split(",")

        # Website find word result
        if complete_text:
            found_words, found_lines = find_words_in_text(complete_text, words_to_find)
            if found_words:
                print("Found words:")
                word_counter = 0
                for word, chapter, line_number, word_position in found_words:
                    word_counter += 1
                print(words_to_find, "was found", word_counter, "times")
                print("\nRelevant verses:")
                for (chapter, line_number) in sorted(found_lines.keys()):
                    print(f"Ch {chapter}: {found_lines[(chapter, line_number)]}") #found_lines[line_number])
            else:
                print("No words found.")
        else:
            print("No text content available.")


            # Find repeated words in book
    elif choice == 2:
        common_words = most_common_words_in_text(combined_text)
        print("Most common words:")
        for word, count in common_words:
            print(f"'{word}': {count}")

    for i in range(5):
        print("-------")