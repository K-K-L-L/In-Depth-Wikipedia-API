# Imports
import discord
import wikipedia
from langdetect import detect
import nltk
import random
import requests
from bs4 import BeautifulSoup
import re

wikipedia.set_lang("ar")

# The files needed for the NLTK library
nltk.download("punkt")
nltk.download('stopwords')


def WebScraper(url):
    # Send a GET request to the URL and get the HTML content
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all the text from the <p> tags (The paragraphs)
    data = str('')
    for p in soup.findAll('p'):
        data += p.get_text()
        data += "\n"
    bs4title = soup.find("title").text
    return data, bs4title


# The SummarizeText method
def SummarizeText(text, ratio):
    sentences = nltk.sent_tokenize(text)
    word_count = len(nltk.word_tokenize(text))
    target_word_count = int(ratio * word_count)
    total_words = 0
    summary = []
    for sent in sentences:
        words = len(nltk.word_tokenize(sent))
        if total_words + words <= target_word_count:
            summary.append(sent)
            total_words += words
        else:
            break
    summary = " ".join(summary)
    return summary

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!ويكي") or message.content.startswith("!wiki"):
        search_query = message.content[6:] # remove "!wiki " from the query
        language = detect(search_query)
        # Set language based on detected language
        if language == "ar":
            await message.channel.send("انتظر...")
            wikipedia.set_lang("ar")
            lang_text = "النص الأصلي\n"
            no_summary_text = "لا يوجد نص مختصر"
            summary = "النص المختصر"
        elif language == "en":
            await message.channel.send("Wait...")
            wikipedia.set_lang(language)
            lang_text = "Original Text\n"
            no_summary_text = "No summary available"
            summary = "Summarized Text"
        try:
            page = wikipedia.page(search_query)
            Wikisummary = wikipedia.summary(search_query)
            NLTKSummary = SummarizeText(Wikisummary, 0.5)

            # Generate response based on language
            if NLTKSummary:
                embed_data = f"""{page.title}\n{page.url}\n\n{lang_text}{Wikisummary}\n\n{summary}\n{NLTKSummary}"""
                embed = discord.Embed(title=page.title, url=page.url,
                                      description=f"**{lang_text}**{Wikisummary}\n\n**{summary}**\n{NLTKSummary}")
            else:
                embed_data = f"""{page.title}\n{page.url}\n\n{lang_text}{Wikisummary}\n\n**{no_summary_text}**"""
                embed = discord.Embed(title=page.title, url=page.url,
                                      description=f"**{lang_text}**{Wikisummary}\n\n**{no_summary_text}**")

            if(len(embed_data) >= 4000):
                RandomNumber = random.randint(0, 99999)
                with open(f"{RandomNumber}.txt", "w", encoding="utf-8") as f:
                    f.write(embed_data)
                with open(f"{RandomNumber}.txt", "rb") as f:
                    file = discord.File(f)
                await message.reply(f"{page.title} {page.url}", file = file)
            else:
                await message.reply(embed = embed)

        except wikipedia.exceptions.PageError:
            try:
                data = WebScraper(f"https://{language}.wikipedia.org/wiki/{search_query}")
                response = WebScraper(f"https://{language}.wikipedia.org/wiki/{search_query}")
                bs4title = WebScraper(f"https://{language}.wikipedia.org/wiki/{search_query}")
            except:
                if language == "ar":
                    await message.reply("لم يتم العثور على الصفحة")
                else:
                    await message.reply("Page was not found")


            try:
                embed = discord.Embed(title=bs4title, url=response,
                description=f"**{lang_text}**{Wikisummary}\n\n**{no_summary_text}**")
            except Exception:
                RandomNumber = random.randint(0, 99999)
                data = tuple(s.replace('\n', '\n') for s in data)
                data = '\n'.join(data)
                data = str(data)
                # Remove brackets with numbers
                data = re.sub(r'\[[0-9]+\]', '', data) 
                # Remove the unnecessary stuff
                data = data.replace("(", "")
                data = data.replace(")", "")
                data = data.replace("'", "")
                data = data.replace("\t", "")
                # Remove the spaces in the first and the end of the text
                data = data.strip()
                # Open a file with a random number
                with open(f"{RandomNumber}.txt", "w", encoding="utf-8") as f:
                    # Write the data
                    f.write(data)
                # Open the file for reading (To send the file through discord)
                with open(f"{RandomNumber}.txt", "rb") as f:
                    file = discord.File(f)
                # Sends the file
                await message.reply(file = file)
        except wikipedia.exceptions.DisambiguationError as e:
            # Limit to 10 options
            options = "\n".join(e.options[:10])
            if language == "ar":
                await message.channel.send(f"خطأ توضيح خيارات: \n{options}")
            elif language == "en":
                await message.channel.send(f"Disambiguation error Options:\n{options}")
client.run("YOUR_BOT_TOKEN")
