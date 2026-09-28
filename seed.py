import memory_ops as mo

NAME = "Sweet Crumbs Bakery"
bank = mo.bank_for(NAME)

mo.save_profile(bank, NAME, "neighbourhood bakery", "Pune",  # change to your city
    "young families, college students and office workers aged 20-40; many prefer eggless options",
    "Instagram and Facebook")

posts = [
 ("2026-08-04","19:00","Instagram","Reel","Behind the scenes: kneading sourdough at 5am",312,41,58,4800,"People loved the process shots and asked when sourdough is available."),
 ("2026-08-07","11:00","Instagram","Photo","Flat 20% off on all cakes this weekend!",45,3,1,900,"Discount post felt salesy; a couple of followers unfollowed."),
 ("2026-08-12","19:30","Instagram","Reel","Watch us frost a chocolate truffle cake",280,36,44,4100,"Several comments asked for an eggless version."),
 ("2026-08-16","08:00","Instagram","Photo","Sunday morning croissants are here",60,5,2,1100,"Low engagement; followers seem inactive on Sunday mornings."),
 ("2026-08-21","18:45","Instagram","Story poll","Which flavour next: mango or pistachio?",120,62,9,2300,"Strong participation; mango won with about 70% of votes."),
 ("2026-08-28","12:00","Facebook","Photo","New eggless mango cake launched",95,22,15,2600,"Many said they would order for birthdays and asked about delivery to nearby colonies."),
 ("2026-09-05","19:00","Instagram","Reel","Customer surprise: birthday cake reveal",350,52,71,6200,"Customer reaction reels perform best; people tagged their friends."),
 ("2026-09-11","17:00","Instagram","Carousel","Ganesh Chaturthi modak box preview",210,30,40,3900,"Preview posted 3 days before the festival drove 18 pre-orders through DMs."),
 ("2026-09-14","10:00","Instagram","Photo","Happy Ganesh Chaturthi!",70,4,3,1300,"Generic greeting on the festival day itself got low engagement."),
 ("2026-09-20","19:15","Instagram","Reel","Packing festive gift boxes",240,27,33,3700,"Good engagement; people asked for prices in the comments."),
]
for p in posts:
    mo.save_post(bank, *p)
    print("saved post:", p[4])

mo.save_event(bank, "Diwali 2025", "2025-10-20",
    "Festive gift hampers previewed 5 days before sold out; orders peaked in the 7 days before Diwali.")
mo.save_event(bank, "Diwali 2026", "2026-11-08",
    "Upcoming festival. Last year hampers sold out when previewed early.")
mo.save_event(bank, "Christmas 2026", "2026-12-25",
    "Upcoming. Plum cakes and eggless plum cakes are expected demand.")

print("Done! Bank:", bank)