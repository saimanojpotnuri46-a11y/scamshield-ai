"""
ScamShield Dataset Generator
Generates realistic, synthetic benchmark datasets for training and evaluating
NLP scam detection models (mimicking SMS, WhatsApp, and email scams).
"""

import os
import random
import re
import pandas as pd

# Set fixed seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

CATEGORIES = [
    "legitimate",
    "bank_impersonation",
    "delivery_fraud",
    "job_scam",
    "investment_crypto",
    "lottery_reward",
    "government_police",
    "tech_support"
]

# Legitimate templates (Ham)
LEGITIMATE_TEMPLATES = [
    "Your OTP for login to OCBC Digital is {otp}. Valid for 3 mins. Never share your OTP with anyone, including bank staff.",
    "DBS: SGD {amount} was charged to your card ending {last4} at {merchant} on {date}. If unauthorized, call the number on the back of your card.",
    "Hi, your appointment with Dr. {doctor} at National University Hospital is confirmed for {date} at {time}. Reply N to reschedule.",
    "Your SingPost parcel {tracking} has been delivered to your doorstep. Thank you for using SingPost.",
    "Hey! Are we still meeting for lunch at {time} tomorrow at {location}? Let me know!",
    "Hi mom, I will be home a bit late today around 8pm. Please don't wait for dinner.",
    "Your Grab ride with driver {driver} ({vehicle}) is arriving in 3 mins. Destination: {destination}.",
    "UOB Transaction Alert: S${amount} transferred via PayNow to {name} on {date}. Ref: {ref_id}.",
    "Your package from Amazon order #{order_id} is out for delivery today. Track in the official Amazon app.",
    "Reminder: Your library book '{book_title}' is due in 3 days. Renew online at nlb.gov.sg or return to any public library.",
    "Hey team, the sprint planning meeting has been moved to Thursday 2pm. Meeting link is on our internal calendar.",
    "Your verification code for Netflix is {otp}. Do not share this code. We never ask for this code via call or text.",
    "DHL Express: Shipment {tracking} is scheduled for delivery today between 14:00 and 18:00. No signature required.",
    "Dear customer, your StarHub bill for account {acc_num} of ${amount} is ready. View and pay securely via the StarHub App.",
    "Can you please send me the slide deck from yesterday's presentation when you get a chance? Thanks!",
    "Your Foodpanda order from {merchant} is being prepared and will arrive in approximately 25-35 mins.",
    "SPF Advisory: Low-crime does not mean no crime. Stay vigilant against online scammers. Learn more at scamshield.gov.sg.",
    "Hey, just saw your message. Yes, let's catch up over coffee this weekend. Saturday works best for me.",
    "Your flight {flight} to {destination} departs at {time} from Terminal 3. Online check-in is now open.",
    "Your gym membership at {gym_name} will renew on {date}. Your monthly charge is ${amount}."
]

# Bank Impersonation templates
BANK_SCAM_TEMPLATES = [
    "URGENT: DBS Alert! Unauthorized login from IP 192.168.1.102 detected. Verify your account immediately to prevent permanent suspension: {url}",
    "OCBC Bank: Your digital token has expired today. Re-activate your access now at {url} to avoid interruption to banking services.",
    "UOB Security Notice: A suspicious transaction of SGD {amount} to overseas account is pending. Cancel transaction now: {url}",
    "Citibank Alert: Your credit card ending {last4} has been locked due to suspicious attempts. Unlock immediately: {url}",
    "Standard Chartered: Important update required on your account KYC. Complete verification within 12 hours: {url}",
    "HSBC Notice: Unusual withdrawal of ${amount} detected. If this was not you, submit dispute request immediately: {url}",
    "Wells Fargo Fraud Alert: Card deactivated. Click to verify your identity and restore card privileges: {url}",
    "DBS PayLah: You received SGD {amount} from an unknown sender. Claim fund into your bank account here: {url}",
    "Chase Alert: Suspicious debit attempt of ${amount}. Reply YES if you, or click {url} to secure account immediately.",
    "Bank Security: Action required. Account #{acc_num} flagged for AML compliance review. Submit documents here: {url}"
]

# Delivery Fraud templates
DELIVERY_SCAM_TEMPLATES = [
    "SingPost: Your package {tracking} is held at our distribution hub due to unpaid customs fee of ${fee}. Pay fee to release: {url}",
    "DHL Express: Delivery attempt failed as nobody was home. Incomplete address detected. Update address within 24h: {url}",
    "FedEx: Package #{tracking} requires customs clearance fee of ${fee}. Pay now to avoid package return: {url}",
    "USPS: Your parcel has arrived at our sorting facility but cannot be dispatched due to missing house number. Confirm here: {url}",
    "NinjaVan: Failed delivery attempt. Please confirm your delivery date and postal code to reschedule: {url}",
    "UPS Notification: Parcel #{tracking} is held at terminal. Outstanding clearance duty ${fee}. Complete payment: {url}",
    "Speedpost Alert: Package status: Delayed. Please update your delivery preferences and pay re-delivery charge: {url}",
    "Amazon Logistics: We tried to deliver your parcel #{order_id} today. Please reschedule and pay redelivery fee at {url}"
]

# Job Scam templates
JOB_SCAM_TEMPLATES = [
    "Earn $200-$600 daily working from home! Simple task: like YouTube videos and review products. No experience needed. Contact WhatsApp: {phone}",
    "Shopee Part-time Recruitment: Looking for online order processing assistants. Daily payout S${amount}. Age 21+. PM WhatsApp {phone}",
    "Amazon Remote Task Agent: Earn SGD 300 to 800 per day! Work 30 mins from phone. Instant payouts. Register: {url}",
    "Lazada Official HR: We have urgent vacancies for remote product rating agents. Daily salary paid directly via PayNow. Chat WhatsApp: {phone}",
    "Tiktok Partner Program: Earn cash by liking videos. Get $50 bonus upon registration. Daily income up to $500. Message HR: {phone}",
    "Global E-Commerce Task: Complete simple rating surveys and earn up to $450/day. Contact telegram @{telegram_handle} or WhatsApp {phone}",
    "Work from anywhere! Google Map reviews task paying $15-$30 per review. Fast payout. Limited slots available. Join: {url}"
]

# Investment & Crypto Scam templates
INVESTMENT_SCAM_TEMPLATES = [
    "Exclusive VIP Crypto Signals! Guaranteed 300% to 500% returns in 7 days using automated AI quant bot. Join Telegram @{telegram_handle} or {url}",
    "Elon Musk Tesla Giveaway: Celebrating new AI breakthrough! Send 0.1 BTC to receive 0.5 BTC instantly. Double your crypto now: {url}",
    "Goldman Sachs FX Program: Turn $500 into $12,500 within 2 weeks with 100% money-back guarantee. WhatsApp our senior analyst at {phone}",
    "Binance VIP Invitation: You have been selected for 80% staking APY promo. Claim promotional liquidity tokens: {url}",
    "Passive income guaranteed! Invest in green energy cloud mining. Daily return 5.8% withdrawable anytime. Register at {url}",
    "Crypto Arbitrage Alert: Risk-free guaranteed daily yield of 12%. Over 50,000 members profiting. Access platform: {url}",
    "Exclusive Pre-sale Token offering: 50x guaranteed return on launch! Buy presale tokens before listing: {url}"
]

# Lottery & Reward Scam templates
LOTTERY_SCAM_TEMPLATES = [
    "Congratulations! Your phone number won $250,000 in the Annual Mobile Lucky Draw. Claim ticket #{ref_id} at {url} or call {phone}",
    "Government Cost-of-Living Payout: You have an uncollected cash voucher of SGD {amount}. Disburse immediately to PayNow: {url}",
    "FairPrice Voucher Promo: You have been selected for a free $300 FairPrice grocery voucher. Answer 3 questions to claim: {url}",
    "Apple Anniversary Giveaway: You are the lucky winner of iPhone 16 Pro Max! Pay shipping fee of ${fee} to receive: {url}",
    "Shell Fuel Rebate: You have $150 unused fuel rewards expiring tonight. Convert to cash rebate now: {url}",
    "StarHub Loyalty Reward: You have 8,920 unredeemed loyalty points expiring today. Redeem for Dyson vacuum or cash: {url}"
]

# Government & Police Scam templates
GOV_POLICE_SCAM_TEMPLATES = [
    "Singapore Police Force Notice: An arrest warrant has been issued under your IC for transnational money laundering. Contact Inspector Tan immediately at {phone}",
    "IRAS Tax Warning: You have overdue income tax penalties of SGD {amount}. Failure to pay within 24h will result in asset seizure and court summons: {url}",
    "High Court of Justice: Subpoena summons issued in criminal case #{ref_id}. View court documents and defense deadline: {url}",
    "Ministry of Health (MOH) Notice: Your name is linked to unauthorized purchase of controlled medicine. Call investigation officer at {phone}",
    "Interpol Red Notice Warning: Your passport has been flagged for criminal investigation. Call regional desk at {phone} to clear name.",
    "Customs Agency: Contraband package intercepted in your name. Respond within 6 hours to prevent immediate police raid: {phone}"
]

# Tech Support Scam templates
TECH_SUPPORT_SCAM_TEMPLATES = [
    "Microsoft Security Alert: Critical Trojan virus detected on your Windows PC! Credit card details leaking. Call Toll-Free {phone} immediately.",
    "Apple ID Warning: Your Apple ID has been suspended due to unauthorized login attempts from China. Verify identity now: {url}",
    "Google Account Security: Someone just accessed your Gmail from unfamiliar device. If not you, secure your account immediately: {url}",
    "Norton 360: Your annual subscription has auto-renewed for $399.99. If you did not authorize this charge, call {phone} for immediate refund.",
    "McAfee Antivirus: 5 viruses detected! System license expired. PC damaged. Renew protection immediately at {url}",
    "Meta Support: Your Facebook and Instagram accounts are scheduled for deletion for copyright infringement. Appeal here: {url}"
]

# Suspicious fake URLs and parameters
SUSPICIOUS_DOMAINS = [
    "http://dbs-secure-verify.xyz",
    "http://ocbc-auth-portal.online",
    "http://uob-token-update.cc",
    "http://singpost-tracking-fees.top",
    "http://dhl-express-redelivery.link",
    "http://fedex-parcel-update.work",
    "http://iras-tax-clearance.vip",
    "http://appleid-security-login.club",
    "http://gov-payout-claim.site",
    "http://crypto-vault-multiplier.live",
    "http://192.168.1.185/bank/login.php",
    "http://bit.ly/claim-sg-grant",
    "http://tinyurl.com/parcel-verify-duty",
    "http://chase-security-fraud-dept.com",
    "http://wellsfargo-debit-reactivate.xyz"
]

SUSPICIOUS_PHONES = [
    "+65 8921 4452",
    "+65 9182 3341",
    "+65 6712 9012",
    "+65 8290 1198",
    "+1-800-419-0921",
    "+44 7911 123456",
    "+60 11-2384-9912",
    "+65 9445 1029"
]

MERCHANTS = ["Cold Storage", "FairPrice", "Shopee SG", "Lazada", "Uniqlo", "GrabFood", "Shell Station", "Netflix"]
NAMES = ["Tan Wei Ming", "Sarah Lim", "Kumar S/O Raja", "David Wong", "Jessica Chen", "Ahmad Bin Ibrahim"]
DESTINATIONS = ["Marina Bay Sands", "Changi Airport T3", "Orchard Central", "Jurong East MRT", "Tampines Mall"]

def get_random_date():
    day = random.randint(1, 28)
    month = random.choice(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"])
    return f"{day:02d} {month}"

def get_random_time():
    hour = random.randint(9, 21)
    minute = random.choice(["00", "15", "30", "45"])
    return f"{hour:02d}:{minute}"

def generate_legitimate_sample():
    template = random.choice(LEGITIMATE_TEMPLATES)
    text = template.format(
        otp=f"{random.randint(100000, 999999)}",
        amount=f"{random.randint(10, 350)}.{random.choice(['00', '20', '50', '80', '95'])}",
        last4=f"{random.randint(1000, 9999)}",
        merchant=random.choice(MERCHANTS),
        date=get_random_date(),
        doctor=random.choice(["Lee", "Tan", "Koh", "Smith", "Rahman"]),
        time=get_random_time(),
        tracking=f"SG{random.randint(10000000, 99999999)}",
        location=random.choice(["Jewel Changi", "Bugis Junction", "Raffles Place", "VivoCity"]),
        driver=random.choice(["Ah Seng", "Rafi", "Ken", "Marcus"]),
        vehicle=f"S{random.choice(['K', 'L', 'M'])}{random.randint(1000, 9999)}{random.choice(['A', 'B', 'C', 'X', 'Y'])}",
        destination=random.choice(DESTINATIONS),
        name=random.choice(NAMES),
        ref_id=f"TXN{random.randint(100000, 999999)}",
        order_id=f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}",
        book_title=random.choice(["Thinking Fast and Slow", "Clean Code", "Design Patterns", "Atomic Habits"]),
        acc_num=f"88{random.randint(100000, 999999)}",
        flight=f"SQ{random.randint(100, 999)}",
        gym_name=random.choice(["Fitness First", "Anytime Fitness", "Virgin Active"])
    )
    return {
        "text": text,
        "label": "ham",
        "category": "legitimate",
        "urgency_level": "low",
        "contains_url": 1 if "http" in text or ".gov.sg" in text else 0,
        "contains_phone": 1 if re.search(r"\+?\d[\d -]{7,}\d", text) else 0
    }

def apply_scam_obfuscation(text):
    """Optionally apply realistic adversarial leetspeak/typos used by scammers."""
    prob = random.random()
    if prob < 0.25:
        # Leetspeak / character substitutions
        subs = [("o", "0"), ("e", "3"), ("a", "@"), ("i", "1"), ("s", "$")]
        chosen_sub = random.choice(subs)
        # substitute only occasionally in words like account or verify
        words = text.split()
        new_words = []
        for w in words:
            if w.lower() in ["account", "verify", "click", "urgent", "update", "suspended"]:
                w = w.replace(chosen_sub[0], chosen_sub[1])
            new_words.append(w)
        text = " ".join(new_words)
    return text

def generate_scam_sample(category):
    url = random.choice(SUSPICIOUS_DOMAINS)
    phone = random.choice(SUSPICIOUS_PHONES)
    fee = f"{random.randint(1, 9)}.{random.choice(['50', '90', '99', '20'])}"
    amount = f"{random.randint(300, 9500):,}"
    last4 = f"{random.randint(1000, 9999)}"
    tracking = f"RR{random.randint(100000000, 999999999)}SG"
    ref_id = f"CASE-{random.randint(1000, 9999)}"
    acc_num = f"{random.randint(1000000000, 9999999999)}"
    order_id = f"{random.randint(100, 999)}-{random.randint(1000000, 9999999)}"
    telegram_handle = random.choice(["official_wealth_bot", "sg_crypto_admin", "task_hr_manager", "invest_expert_sg"])

    urgency_level = "high"
    if category == "bank_impersonation":
        template = random.choice(BANK_SCAM_TEMPLATES)
        urgency_level = random.choice(["high", "critical"])
    elif category == "delivery_fraud":
        template = random.choice(DELIVERY_SCAM_TEMPLATES)
        urgency_level = random.choice(["medium", "high"])
    elif category == "job_scam":
        template = random.choice(JOB_SCAM_TEMPLATES)
        urgency_level = random.choice(["low", "medium"])
    elif category == "investment_crypto":
        template = random.choice(INVESTMENT_SCAM_TEMPLATES)
        urgency_level = random.choice(["medium", "high"])
    elif category == "lottery_reward":
        template = random.choice(LOTTERY_SCAM_TEMPLATES)
        urgency_level = random.choice(["medium", "high"])
    elif category == "government_police":
        template = random.choice(GOV_POLICE_SCAM_TEMPLATES)
        urgency_level = "critical"
    elif category == "tech_support":
        template = random.choice(TECH_SUPPORT_SCAM_TEMPLATES)
        urgency_level = random.choice(["high", "critical"])
    else:
        template = random.choice(BANK_SCAM_TEMPLATES)

    text = template.format(
        url=url,
        phone=phone,
        fee=fee,
        amount=amount,
        last4=last4,
        tracking=tracking,
        ref_id=ref_id,
        acc_num=acc_num,
        order_id=order_id,
        telegram_handle=telegram_handle
    )

    text = apply_scam_obfuscation(text)

    return {
        "text": text,
        "label": "scam",
        "category": category,
        "urgency_level": urgency_level,
        "contains_url": 1 if "http" in text else 0,
        "contains_phone": 1 if re.search(r"\+?\d[\d -]{7,}\d", text) else 0
    }

def generate_dataset(n_samples=1600):
    """
    Generate dataset with balanced proportions:
    40% Legitimate (Ham)
    60% Scam distributed across 7 attack typologies
    """
    scam_categories = [c for c in CATEGORIES if c != "legitimate"]
    records = []

    n_ham = int(n_samples * 0.40)
    n_scam = n_samples - n_ham
    scams_per_cat = n_scam // len(scam_categories)

    # Generate legitimate records
    for _ in range(n_ham):
        records.append(generate_legitimate_sample())

    # Generate scam records
    for cat in scam_categories:
        for _ in range(scams_per_cat):
            records.append(generate_scam_sample(cat))

    # Add remainder scams if any
    while len(records) < n_samples:
        records.append(generate_scam_sample(random.choice(scam_categories)))

    random.shuffle(records)

    # Assign IDs
    for idx, rec in enumerate(records):
        rec["id"] = f"MSG_{idx+1:05d}"

    df = pd.DataFrame(records)
    # Reorder columns
    df = df[["id", "text", "label", "category", "urgency_level", "contains_url", "contains_phone"]]
    return df

def save_benchmark_splits(output_dir):
    """Generates train, val, test_ground_truth, and test_unlabeled splits."""
    os.makedirs(output_dir, exist_ok=True)

    print("Generating ScamShield NLP Challenge Dataset...")
    full_df = generate_dataset(n_samples=1800)

    # Split into Train (1100), Val (350), Test (350)
    train_df = full_df.iloc[:1100].copy()
    val_df = full_df.iloc[1100:1450].copy().reset_index(drop=True)
    test_df = full_df.iloc[1450:].copy().reset_index(drop=True)

    train_path = os.path.join(output_dir, "train.csv")
    val_path = os.path.join(output_dir, "val.csv")
    test_gt_path = os.path.join(output_dir, "test_ground_truth.csv")
    test_unlabeled_path = os.path.join(output_dir, "test_unlabeled.csv")

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_gt_path, index=False)

    # Unlabeled test for challenge participants
    test_unlabeled_df = test_df[["id", "text"]].copy()
    test_unlabeled_df.to_csv(test_unlabeled_path, index=False)

    print(f"Datasets generated successfully:")
    print(f" - Train: {train_path} ({len(train_df)} rows)")
    print(f" - Val:   {val_path} ({len(val_df)} rows)")
    print(f" - Test Ground Truth: {test_gt_path} ({len(test_df)} rows)")
    print(f" - Test Unlabeled (Participants): {test_unlabeled_path} ({len(test_unlabeled_df)} rows)")
    print(f"Category Distribution in Train:\n{train_df['category'].value_counts()}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_benchmark_splits(current_dir)
