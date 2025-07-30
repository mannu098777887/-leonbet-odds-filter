# -leonbet-odds-filter
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import time
import pandas as pd

# Set up Chrome driver with headless option
def get_driver():
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)
    return driver

# Scrape Leon Bet odds
def scrape_leon_odds():
    driver = get_driver()
    driver.get("https://leon.bet/en/bets/soccer")
    time.sleep(5)  # Let the page load

    matches = []

    try:
        events = driver.find_elements(By.CSS_SELECTOR, '[data-qa="sportsbook-event"]')
        for event in events:
            try:
                teams = event.find_element(By.CSS_SELECTOR, '[data-qa="sportsbook-event-header-names"]')
                team_text = teams.text.replace("\n", " vs ")

                odds_elements = event.find_elements(By.CSS_SELECTOR, '[data-qa="outcome-odds"]')
                odds = [float(o.text) for o in odds_elements if o.text.replace('.', '', 1).isdigit()]

                if len(odds) >= 5:
                    over_05 = odds[-3]
                    over_15 = odds[-1]

                    if 1.08 <= over_05 <= 1.11 and 1.40 <= over_15 <= 1.44:
                        matches.append({
                            "Match": team_text,
                            "Over 0.5 Odds": over_05,
                            "Over 1.5 Odds": over_15
                        })
            except:
                continue
    except:
        st.error("Error fetching data from Leon Bet.")
    finally:
        driver.quit()

    return pd.DataFrame(matches)

# Streamlit UI
st.set_page_config(page_title="Leon Bet Odds Filter", layout="centered")
st.title("Leon Bet Odds Filter")
st.write("Showing matches with Over 0.5 odds between 1.08–1.11 and Over 1.5 odds between 1.40–1.44")

if st.button("Fetch Matches"):
    with st.spinner("Fetching matches, please wait..."):
        df = scrape_leon_odds()
    if not df.empty:
        st.success(f"Found {len(df)} matching matches!")
        st.dataframe(df)
    else:
        st.warning("No matches found with the specified odds.")
  
