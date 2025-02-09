import pandas as pd

# Create sample tourism guide entries in English
tourism_guides = [
    {
        "text": "Dubrovnik is a stunning city in southern Croatia, famous for its impressive walls dating back to the 13th century. The Old Town of Dubrovnik, a UNESCO World Heritage site, is surrounded by walls stretching 1940 meters. The main street Stradun runs through the heart of the old town, lined with numerous restaurants, cafes, and shops. Fort Lovrijenac, perched on a 37-meter-high cliff, offers spectacular views of the city and the Adriatic Sea. During summer months, the city hosts the renowned Dubrovnik Summer Festival from July 10th to August 25th."
    },
    {
        "text": "Split, Croatia's second-largest city, is renowned for its 4th-century Diocletian's Palace. The palace was built as a residence for the Roman Emperor Diocletian and today forms the core of the city center. Within the palace walls stands the Cathedral of Saint Domnius, originally Diocletian's mausoleum. The Riva, Split's waterfront promenade, stretches along the harbor and is a popular spot for walking and socializing. Nearby, Marjan Hill is a protected area covered in Mediterranean vegetation, offering numerous walking trails and viewpoints."
    },
    {
        "text": "Plitvice Lakes National Park is the largest and oldest national park in Croatia. The park is famous for its 16 lakes of varying sizes, interconnected by waterfalls. The lakes are known for their unique turquoise color, created by special geological conditions and the presence of different minerals. The park features 18 kilometers of wooden walkways and bridges. The best time to visit is from spring to autumn, though the park is open year-round. Tickets can be purchased at park entrances, and guided tours are available."
    },
    {
        "text": "Rovinj is a picturesque town on the western coast of Istria. The old town is situated on a peninsula, with narrow streets leading to St. Euphemia's Church at the hilltop. The church features the tallest bell tower on the Istrian coast, reaching 60 meters. The town is known for its fish market, art scene, and numerous restaurants serving traditional Istrian cuisine. Nearby lies an archipelago of 13 islands, with Red Island and St. Catherine's Island being the most famous. The surrounding area is renowned for olive cultivation and production of high-quality olive oil."
    },
    {
        "text": "Zadar is a city rich in history on the Dalmatian coast. Popular city attractions include the Sea Organ, a unique architectural installation that produces music using sea waves, and the Sun Salutation, a light installation creating an impressive light show during sunset. The 9th-century Church of St. Donatus is one of the city's most recognizable symbols. Zadar's Forum is the largest Roman square on the eastern side of the Adriatic. The city is also famous for its beautiful sunsets, which Alfred Hitchcock described as the most beautiful in the world."
    },
    {
        "text": "Hvar is one of Croatia's most popular islands, known for its Mediterranean climate and record number of sunny hours. The town of Hvar, located on the island's southwestern coast, has a vibrant harbor and historic center. Fortica Fortress (Spanish Fortress) dominates the town and provides spectacular views of the Pakleni Islands. The island is famous for its lavender fields, vineyards, and olive groves. The Stari Grad Plain, a UNESCO World Heritage site, is the best-preserved ancient Greek land parcel system in the Mediterranean."
    },
    {
        "text": "Zagreb, Croatia's capital, blends Central European history with a Mediterranean lifestyle. The Upper Town, Zagreb's historic district, is home to St. Mark's Church with its distinctive colorful roof, the Stone Gate, and the Museum of Broken Relationships. The Lower Town features elegant 19th-century buildings, Ban Jelačić Square, and the Lenuci Horseshoe, a series of squares and parks. Dolac, the central city market, is the best place to experience local gastronomy. Maksimir, Zagreb's oldest public park, is perfect for escaping the city bustle."
    },
    {
        "text": "The Krapina Neanderthal Museum is one of Croatia's most modern museums. Opened in 2010, the museum presents the evolution of life on Earth with special emphasis on the Neanderthal period. The Hušnjakovo site, where Neanderthal remains were discovered, is located right next to the museum. The museum receives over 100,000 visitors annually. The permanent exhibition includes life-sized reconstructions of Neanderthals."
    },
    {
        "text": "Opatija is often called the 'Pearl of the Adriatic' and was Croatia's first tourist destination. Hotel Kvarner, built in 1884, was the first hotel on the eastern Adriatic coast. The Lungomare, a famous coastal promenade, extends 12 kilometers from Volosko to Lovran. Angiolina Park is home to over 150 plant species from around the world. Villa Angiolina represents the beginning of tourism in Opatija."
    },
    {
        "text": "Varaždin is a city of baroque, music, and flowers. The Old Town Castle is a medieval fortress converted into a palace. Varaždin Cemetery, designed by Herman Haller, is considered one of the most beautiful in Europe. Špancirfest, a traditional street festival, takes place in late August. The City Hall is one of the oldest in Europe, built in the 16th century."
    },
    {
        "text": "Kornati National Park consists of 89 islands, islets, and reefs. The park area covers about 220 square kilometers. The most notable feature of Kornati are the 'crowns', steep cliffs facing the open sea. Murter is the main departure point for visiting the park. Diving is one of the most popular activities in the park."
    },
    {
        "text": "Kopački Rit is the largest wetland area in Croatia. The Nature Park is home to over 290 bird species. The best time to visit is spring and autumn during bird migration. Wooden walkways allow visitors to observe wildlife up close. The park is located at the confluence of the Drava and Danube rivers."
    },
    {
        "text": "Motovun is a picturesque small town in central Istria. The town walls are 1052 meters long and provide panoramic views of the Mirna River valley. The Motovun Forest is famous for truffles, especially the white truffle. The Motovun Film Festival is held every year in late July. The 15th-century town gate serves as the main entrance to the old town."
    },
    {
        "text": "Trogir, located on a small island between the mainland and Čiovo, is a remarkable example of medieval urban continuity. The historic city center is a UNESCO World Heritage site known for its Venetian architecture. The Cathedral of St. Lawrence, built between the 13th and 15th centuries, features the famous Portal of Radovan from 1240. The city's Kamerlengo Fortress, constructed in the 15th century, offers panoramic views of the surrounding area. Trogir's charming promenade is lined with luxury yachts and traditional fishing boats, creating a perfect blend of historic charm and modern maritime life."
    },
    {
        "text": "The Krka National Park, established in 1985, is a natural karst phenomenon located in central Dalmatia. The park is famous for its seven magnificent waterfalls, with Skradinski Buk being the longest and most visited waterfall on the Krka River, extending 45.7 meters. The park includes the Franciscan Monastery of Our Lady of Mercy and the Orthodox Monastery of Krka, both situated on Visovac Island. Visitors can explore 109 square kilometers of pristine nature through various walking trails and boat excursions."
    },
    {
        "text": "Šibenik, the oldest native Croatian city on the Adriatic, is home to two UNESCO World Heritage sites. The Cathedral of St. James, built between 1431 and 1536, is unique for being constructed entirely of stone without using any mortar. The St. Nicholas Fortress, built in 1540, served as a crucial defensive structure protecting the city's port. The city's Medieval Monastery Garden of St. Lawrence, recently renovated, features traditional Mediterranean herbs and offers educational programs about medieval medicine."
    },
    {
        "text": "The Pula Arena, located in Pula, is one of the best-preserved Roman amphitheaters in the world. Built between 27 BC and 68 AD, it is the sixth-largest surviving Roman arena and could host up to 23,000 spectators. The amphitheater is 132.45 meters long and 105.1 meters wide, with walls rising 32.45 meters high. Today, it hosts various cultural events, including the Pula Film Festival, concerts, and opera performances. The underground passages, once used for gladiator preparations, now house a permanent exhibition about olive growing and wine production in ancient Istria."
    },
    {
        "text": "The Brijuni Islands National Park consists of 14 islands off the coast of Istria. The largest island, Veliki Brijun, features a Safari Park housing animals that were gifts to former Yugoslav president Tito from world leaders. The islands contain over 200 dinosaur footprints, dating back to the Cretaceous period. Archaeological sites include Roman and Byzantine ruins, while the 1,600-year-old olive tree still produces olives. The former presidential residence now serves as a hotel, and visitors can tour the islands by tourist train or electric cars."
    },
    {
        "text": "Rastoke, often called the 'Little Plitvice', is a historic watermill village where the Slunjčica River meets the Korana River. The village features 23 waterfalls and several preserved watermills, some dating back to the 17th century. Traditional houses are built directly over the water on travertine rocks, creating a unique architectural harmony with nature. Local restaurants serve freshwater fish specialties, and visitors can learn about the traditional milling process through demonstrations by local millers."
    },
    {
        "text": "The Paklenica National Park, established in 1949, is Croatia's premier rock-climbing destination. The park features two impressive canyons: Velika Paklenica and Mala Paklenica. The Manita peć cave, located 570 meters above sea level, extends 175 meters deep into the mountain. The park contains 150 kilometers of hiking trails and over 500 climbing routes. The Paklenica mill and Marasović rural estate showcase traditional architecture and lifestyle of the Velebit mountain region."
    },
    {
        "text": "Samobor, a picturesque town near Zagreb, is famous for its carnival traditions dating back to 1827. The town is renowned for its cream cake, 'Samoborska kremšnita', which has been made since 1923 using a secret recipe. The Old Town fortress, built in the 13th century, offers panoramic views of the surrounding Samobor mountains. The town's Crystal Palace, built in 1764, now serves as a cultural center. Samobor's bermet, a special aromatic wine, and mustarda, a spicy condiment, are protected geographical products."
    },
    {
        "text": "The island of Mljet, known as Croatia's greenest island, has a National Park covering its western third. The park features two salt lakes, Veliko and Malo Jezero, with a Benedictine monastery on an isle in Veliko Jezero. The monastery, built in the 12th century, is now a restaurant and café. The island has 131 kilometers of coastline and numerous caves, including Odysseus Cave, linked to the legendary hero's seven-year stay. The native Mljet honeybee produces unique sage honey, and the waters around the island contain rich coral colonies."
    },
    {
        "text": "Osijek, the largest city in Slavonia, is known for its Habsburg-era Tvrđa fortress. Built between 1712 and 1721, the fortress is the best-preserved baroque military complex in Croatia. The city's suspension pedestrian bridge, built in 1981, spans 210 meters across the Drava River. Osijek's Kapucinska Street features stunning Art Nouveau architecture from the early 20th century. The Sakuntala Park, created in 1890, contains a famous statue by Robert Frangeš-Mihanović, depicting a scene from ancient Indian literature."
    },
    {
        "text": "The Blue Cave on Biševo Island is a natural sea grotto famous for its ethereal blue glow. The cave is 24 meters long, 12 meters high, and up to 15 meters wide. The magical blue light effect occurs between 11 AM and noon when sunlight reflects through an underwater opening. The cave was first described by Baron Eugen von Ransonet in 1884, and today it attracts over 100,000 visitors annually. The only entrance to the cave is by small boat through a narrow opening just 1.5 meters high."
    },
    {
        "text": "The island of Vis, the farthest inhabited island off the Croatian mainland, is known for its rich history and unspoiled nature. The island's Stiniva Beach, voted Europe's best beach in 2016, is accessible through a narrow cliff passage only 4 meters wide. The town of Komiža features traditional fishermen's houses and the Fishermen's Museum housed in a 16th-century Venetian tower. The island is famous for its indigenous white wine variety, Vugava, cultivated since ancient Greek times."
    },
    {
        "text": "The Baranja region is known for its wine-making tradition and unique wetlands. The Kopački Rit Nature Park, often called the European Amazon, is one of the largest preserved wetlands in Europe. The region's wine cellars, carved into loess hills, form the famous 'Wine Roads of Baranja'. The Batina Monument, standing 27 meters tall, commemorates the Battle of Batina from 1944. Traditional Baranja houses feature distinctive white walls with blue borders and exposed wooden beams."
    },
    {
        "text": "Dubrovnik is a stunning city in southern Croatia, famous for its impressive walls dating back to the 13th century. The Old Town of Dubrovnik, a UNESCO World Heritage site, is surrounded by walls stretching 1940 meters. The main street Stradun runs through the heart of the old town, lined with numerous restaurants, cafes, and shops. Fort Lovrijenac, perched on a 37-meter-high cliff, offers spectacular views of the city and the Adriatic Sea. During summer months, the city hosts the renowned Dubrovnik Summer Festival from July 10th to August 25th."
    },
    {
        "text": "Split, Croatia's second-largest city, is renowned for its 4th-century Diocletian's Palace. The palace was built as a residence for the Roman Emperor Diocletian and today forms the core of the city center. Within the palace walls stands the Cathedral of Saint Domnius, originally Diocletian's mausoleum. The Riva, Split's waterfront promenade, stretches along the harbor and is a popular spot for walking and socializing. Nearby, Marjan Hill is a protected area covered in Mediterranean vegetation, offering numerous walking trails and viewpoints."
    }
]

# Create DataFrame
df = pd.DataFrame(tourism_guides)

# Save to CSV
df.to_csv('tourism_guides.csv', index=False)

print("English tourism guides CSV file has been created successfully!")