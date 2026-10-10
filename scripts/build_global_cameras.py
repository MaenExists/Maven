#!/usr/bin/env python3
"""
Global CCTV & Street Surveillance Camera Dataset Generator
Synthesizes and compiles comprehensive worldwide camera network across 320+ metropolitan centers,
transportation corridors, international ports, and strategic checkpoints across 140+ countries.
"""

import json
import os
import random

# Seed for reproducible deterministic coordinates and camera IDs
random.seed(42)

METROPOLITAN_HUBS = [
    # =========================================================================
    # NORTH AMERICA: UNITED STATES
    # =========================================================================
    {"city": "New York City", "country": "USA", "lat": 40.7128, "lon": -74.0060, "count": 35,
     "corridors": ["Times Square 46th St", "Broadway & 42nd St", "Brooklyn Bridge West", "Manhattan Bridge Plaza",
                   "5th Avenue & 59th St", "Grand Central Terminal", "Wall Street Bull", "World Trade Center Plaza",
                   "Lincoln Tunnel Approach", "Holland Tunnel Plaza", "Central Park South", "Queensboro Bridge Ramp",
                   "FDR Drive & 34th St", "West Side Highway & 14th", "SoHo Broadway", "Herald Square 34th St"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Los Angeles", "country": "USA", "lat": 34.0522, "lon": -118.2437, "count": 30,
     "corridors": ["Hollywood Blvd & Highland", "Santa Monica Pier", "Downtown LA 7th & Fig", "Wilshire Blvd Corridor",
                   "Sunset Strip West", "I-405 Sepulveda Pass", "I-10 Santa Monica Fwy", "Venice Beach Boardwalk",
                   "LAX Airport Terminal 4", "Dodger Stadium Gate", "Griffith Observatory Vista", "Century City Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=1x2w4e_zK1s", "stream_type": "youtube"},

    {"city": "San Francisco", "country": "USA", "lat": 37.7749, "lon": -122.4194, "count": 25,
     "corridors": ["Golden Gate Bridge Vista", "Powell & Market Cable Car", "Fisherman's Wharf Pier 39",
                   "Embarcadero & Ferry Building", "Bay Bridge Toll Plaza", "Lombard Street Crooked Way",
                   "Chinatown Dragon Gate", "Union Square North", "Twin Peaks Overlook", "Mission St & 16th"],
     "stream_url": "https://www.youtube.com/watch?v=d_2y1qL2m4E", "stream_type": "youtube"},

    {"city": "Chicago", "country": "USA", "lat": 41.8781, "lon": -87.6298, "count": 25,
     "corridors": ["Michigan Avenue Bridge", "Millennium Park Cloud Gate", "Navy Pier Entrance", "Wacker Drive Riverwalk",
                   "I-90/94 Kennedy Expressway", "State St & Lake", "Willis Tower Skydeck Plaza", "Magnificent Mile"],
     "stream_url": "https://www.youtube.com/watch?v=1x2w4e_zK1s", "stream_type": "youtube"},

    {"city": "Miami", "country": "USA", "lat": 25.7617, "lon": -80.1918, "count": 22,
     "corridors": ["Ocean Drive South Beach", "Biscayne Blvd Downtown", "Brickell Avenue Financial", "PortMiami Gateway",
                   "MacArthur Causeway", "Calle Ocho Little Havana", "Collins Ave 21st St", "Wynwood Walls Arts Corridor"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Las Vegas", "country": "USA", "lat": 36.1699, "lon": -115.1398, "count": 24,
     "corridors": ["Bellagio Fountains Strip", "Fremont Street Experience", "Tropicana & Las Vegas Blvd", "Flamingo Rd Crossing",
                   "Venetian Gondola Canal", "Caesars Palace Plaza", "MGM Grand Crosswalk", "Stratosphere Tower Vista"],
     "stream_url": "https://www.youtube.com/watch?v=4p1g3E_yWl0", "stream_type": "youtube"},

    {"city": "Seattle", "country": "USA", "lat": 47.6062, "lon": -122.3321, "count": 20,
     "corridors": ["Pike Place Market Clock", "Space Needle Plaza", "Alaskan Way Waterfront", "I-5 Ship Canal Bridge",
                   "Pioneer Square", "Westlake Center", "Elliott Bay Marina", "Capitol Hill Broadway"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Washington D.C.", "country": "USA", "lat": 38.9072, "lon": -77.0369, "count": 22,
     "corridors": ["National Mall & Monument", "Pennsylvania Ave NW", "Capitol Hill East Gate", "Dupont Circle Plaza",
                   "K Street Corridor", "Georgetown M Street", "Key Bridge Potomac", "Tidal Basin Jefferson"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Houston", "country": "USA", "lat": 29.7604, "lon": -95.3698, "count": 20,
     "corridors": ["Downtown Main St", "Galleria Post Oak", "I-610 West Loop", "Texas Medical Center", "I-45 Pierce Elevated"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Dallas", "country": "USA", "lat": 32.7767, "lon": -96.7970, "count": 18,
     "corridors": ["Dealey Plaza Elm St", "Arts District Flora St", "Uptown McKinney Ave", "I-35E Stemmons Fwy"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Austin", "country": "USA", "lat": 30.2672, "lon": -97.7431, "count": 16,
     "corridors": ["Congress Avenue Bridge", "6th Street Entertainment", "Texas State Capitol Plaza", "Rainey Street Corridor"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "San Antonio", "country": "USA", "lat": 29.4241, "lon": -98.4936, "count": 16,
     "corridors": ["Alamo Plaza Historic", "Paseo del Rio Riverwalk", "Market Square El Mercado", "Tower of Americas Vista"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Philadelphia", "country": "USA", "lat": 39.9526, "lon": -75.1652, "count": 20,
     "corridors": ["City Hall Broad St", "Independence Hall Chestnut St", "Benjamin Franklin Parkway", "South Street Commercial"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Phoenix", "country": "USA", "lat": 33.4484, "lon": -112.0740, "count": 18,
     "corridors": ["Central Ave Downtown", "Camelback Road Corridor", "Roosevelt Row Arts", "I-10 Papago Freeway"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "San Diego", "country": "USA", "lat": 32.7157, "lon": -117.1611, "count": 20,
     "corridors": ["Gaslamp Quarter 5th Ave", "Coronado Bridge View", "Balboa Park Plaza", "Pacific Beach Boardwalk"],
     "stream_url": "https://www.youtube.com/watch?v=1x2w4e_zK1s", "stream_type": "youtube"},

    {"city": "Denver", "country": "USA", "lat": 39.7392, "lon": -104.9903, "count": 16,
     "corridors": ["16th Street Mall", "Civic Center Park", "I-25 & Colfax Ave", "Union Station Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Boston", "country": "USA", "lat": 42.3601, "lon": -71.0589, "count": 18,
     "corridors": ["Faneuil Hall Quincy Market", "Boston Common Tremont St", "Boylston St Copley Square", "Zakim Bunker Hill Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Atlanta", "country": "USA", "lat": 33.7490, "lon": -84.3880, "count": 18,
     "corridors": ["Centennial Olympic Park", "Peachtree St Downtown", "Piedmont Park Meadow", "I-75/85 Downtown Connector"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Honolulu", "country": "USA", "lat": 21.3069, "lon": -157.8583, "count": 16,
     "corridors": ["Kalakaua Ave Waikiki Beach", "Kuhio Beach Promenade", "Diamond Head Lookout", "Ala Moana Blvd"],
     "stream_url": "https://www.youtube.com/watch?v=3r2x1w4e_zM", "stream_type": "youtube"},

    {"city": "New Orleans", "country": "USA", "lat": 29.9511, "lon": -90.0715, "count": 16,
     "corridors": ["Bourbon Street French Quarter", "Jackson Square St. Louis Cathedral", "Canal Street Transit", "St. Charles Ave Streetcar"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Nashville", "country": "USA", "lat": 36.1627, "lon": -86.7816, "count": 16,
     "corridors": ["Lower Broadway Honky Tonk", "Ryman Auditorium Plaza", "Gulch 11th Ave", "Cumberland Riverfront Park"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Portland", "country": "USA", "lat": 45.5152, "lon": -122.6784, "count": 16,
     "corridors": ["Pioneer Courthouse Square", "Burnside Bridge Waterfront", "Pearl District NW 10th", "Hawthorne Bridge East"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Minneapolis", "country": "USA", "lat": 44.9778, "lon": -93.2650, "count": 14,
     "corridors": ["Nicollet Mall Transitway", "Stone Arch Bridge Mississippi", "First Avenue Corridor", "Hennepin Ave Downtown"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Detroit", "country": "USA", "lat": 42.3314, "lon": -83.0458, "count": 16,
     "corridors": ["Woodward Avenue Campus Martius", "Detroit Riverwalk Promenade", "Hart Plaza Riverfront", "Ambassador Bridge Approach"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Pittsburgh", "country": "USA", "lat": 40.4406, "lon": -79.9959, "count": 14,
     "corridors": ["Point State Park Fountain", "Smithfield Street Bridge", "Penn Avenue Cultural District", "Mount Washington Overlook"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    {"city": "Anchorage", "country": "USA", "lat": 61.2181, "lon": -149.9003, "count": 12,
     "corridors": ["4th Avenue Downtown", "Cook Inlet Coastal Trail", "Lake Hood Seaplane Base", "Seward Highway South"],
     "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA", "stream_type": "youtube"},

    # =========================================================================
    # NORTH AMERICA: CANADA & MEXICO
    # =========================================================================
    {"city": "Toronto", "country": "Canada", "lat": 43.6532, "lon": -79.3832, "count": 25,
     "corridors": ["Yonge-Dundas Square", "CN Tower Plaza", "Nathan Phillips Square", "Gardiner Expressway", "Bloor-Yorkville", "Harbourfront Centre"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Vancouver", "country": "Canada", "lat": 49.2827, "lon": -123.1207, "count": 20,
     "corridors": ["Robson Street Corridor", "Granville Street Entertainment", "Canada Place Pier", "Lions Gate Bridge North", "English Bay Beach Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Montreal", "country": "Canada", "lat": 45.5017, "lon": -73.5673, "count": 20,
     "corridors": ["Old Port Saint-Paul St", "Sainte-Catherine St", "Place des Arts", "Jacques Cartier Bridge", "Mount Royal Belvédère"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Calgary", "country": "Canada", "lat": 51.0447, "lon": -114.0719, "count": 16,
     "corridors": ["Stephen Avenue Walk", "Calgary Tower Plaza", "Peace Bridge Bow River", "Olympic Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Ottawa", "country": "Canada", "lat": 45.4215, "lon": -75.6972, "count": 16,
     "corridors": ["Parliament Hill Wellington St", "ByWard Market Square", "Rideau Canal Locks", "Confederation Square"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Edmonton", "country": "Canada", "lat": 53.5461, "lon": -113.4938, "count": 14,
     "corridors": ["Churchill Square City Hall", "High Level Bridge", "Whyte Avenue Old Strathcona", "Jasper Avenue Downtown"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Halifax", "country": "Canada", "lat": 44.6488, "lon": -63.5752, "count": 12,
     "corridors": ["Halifax Waterfront Boardwalk", "Citadel Hill Historic Gate", "Spring Garden Road", "Angus L. Macdonald Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A", "stream_type": "youtube"},

    {"city": "Mexico City", "country": "Mexico", "lat": 19.4326, "lon": -99.1332, "count": 26,
     "corridors": ["Zócalo Plaza Mayor", "Paseo de la Reforma & Ángel", "Palacio de Bellas Artes", "Polanco Masaryk", "Coyoacán Centenario", "Chapultepec Bosque Entrance"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Guadalajara", "country": "Mexico", "lat": 20.6597, "lon": -103.3496, "count": 16,
     "corridors": ["Plaza de Armas Cathedral", "Avenida Chapultepec Corridor", "Puente Matute Remus", "Glorieta La Minerva"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Monterrey", "country": "Mexico", "lat": 25.6866, "lon": -100.3161, "count": 16,
     "corridors": ["Macroplaza Faro del Comercio", "Paseo Santa Lucía Riverwalk", "San Pedro Garza García Financial", "Puente Atirantado"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Cancun", "country": "Mexico", "lat": 21.1619, "lon": -86.8515, "count": 14,
     "corridors": ["Boulevard Kukulcan Hotel Zone", "Playa Delfines Lookout", "Plaza Forum by the Sea", "Puerto Juarez Maritime Ferry"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    # =========================================================================
    # CENTRAL AMERICA & CARIBBEAN
    # =========================================================================
    {"city": "Panama City", "country": "Panama", "lat": 8.9824, "lon": -79.5199, "count": 18,
     "corridors": ["Cinta Costera Coastal Parkway", "Casco Viejo Plaza Mayor", "Panama Canal Miraflores Locks", "Punta Pacifica Towers"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "San Jose", "country": "Costa Rica", "lat": 9.9281, "lon": -84.0907, "count": 14,
     "corridors": ["Avenida Central Pedestrian", "Plaza de la Cultura Teatro Nacional", "Parque La Sabana East", "Paseo Colón Corridor"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Guatemala City", "country": "Guatemala", "lat": 14.6349, "lon": -90.5069, "count": 14,
     "corridors": ["Plaza de la Constitución Palacio", "Paseo de la Sexta Zona 1", "Avenida La Reforma Zona 9", "Zona 10 Zona Viva"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "San Juan", "country": "Puerto Rico", "lat": 18.4655, "lon": -66.1057, "count": 16,
     "corridors": ["Old San Juan Calle Fortaleza", "El Morro Esplanade", "Condado Ashford Avenue", "Isla Verde Beach Walk"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Havana", "country": "Cuba", "lat": 23.1136, "lon": -82.3666, "count": 14,
     "corridors": ["Malecón Seaside Promenade", "Plaza de la Revolución", "El Capitolio Paseo del Prado", "Plaza Vieja Old Havana"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Santo Domingo", "country": "Dominican Republic", "lat": 18.4861, "lon": -69.9312, "count": 14,
     "corridors": ["Zona Colonial Parque Colón", "Malecón George Washington", "Plaza de la Cultura", "Avenida Winston Churchill"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zL", "stream_type": "youtube"},

    # =========================================================================
    # SOUTH AMERICA
    # =========================================================================
    {"city": "São Paulo", "country": "Brazil", "lat": -23.5505, "lon": -46.6333, "count": 28,
     "corridors": ["Avenida Paulista MASP", "Faria Lima Financial Center", "Ibirapuera Park Entrance", "Praça da Sé Cathedral",
                   "Rua 25 de Março Commercial", "Marginal Pinheiros Highway", "Berrini Bridge Estaiada", "Liberdade Japanese Square"],
     "stream_url": "https://www.youtube.com/watch?v=pW7w3g2bM1Q", "stream_type": "youtube"},

    {"city": "Rio de Janeiro", "country": "Brazil", "lat": -22.9068, "lon": -43.1729, "count": 26,
     "corridors": ["Copacabana Beach Posto 4", "Ipanema Beach Posto 9", "Corcovado Christ Redeemer Vista", "Sugarloaf Mountain Urca",
                   "Lapa Arches Square", "Barra da Tijuca Beach", "Maracanã Stadium Gate", "Flamengo Park Coastal Highway"],
     "stream_url": "https://www.youtube.com/watch?v=pW7w3g2bM1Q", "stream_type": "youtube"},

    {"city": "Brasília", "country": "Brazil", "lat": -15.7975, "lon": -47.8919, "count": 16,
     "corridors": ["Praça dos Três Poderes", "Esplanada dos Ministérios", "Ponte JK Paranoá Lake", "Catedral Metropolitana Facade"],
     "stream_url": "https://www.youtube.com/watch?v=pW7w3g2bM1Q", "stream_type": "youtube"},

    {"city": "Buenos Aires", "country": "Argentina", "lat": -34.6037, "lon": -58.3816, "count": 25,
     "corridors": ["Obelisco Avenida 9 de Julio", "Plaza de Mayo Casa Rosada", "Puerto Madero Puente de la Mujer",
                   "Caminito La Boca Historic", "Recoleta Cemetery Junín St", "Palermo Soho Plaza Serrano", "Teatro Colón Libertad St"],
     "stream_url": "https://www.youtube.com/watch?v=6b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Santiago", "country": "Chile", "lat": -33.4489, "lon": -70.6693, "count": 20,
     "corridors": ["Plaza de Armas Cathedral", "Gran Torre Santiago Costanera", "La Moneda Presidential Plaza", "San Cristóbal Funicular", "Providencia Pedro de Valdivia"],
     "stream_url": "https://www.youtube.com/watch?v=6b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Bogotá", "country": "Colombia", "lat": 4.7110, "lon": -74.0721, "count": 20,
     "corridors": ["Plaza de Bolívar Congress", "Monserrate Sanctuary Mountain", "Carrera 7 Pedestrian", "Zona T Entertainment", "Parque de la 93"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Medellín", "country": "Colombia", "lat": 6.2442, "lon": -75.5812, "count": 18,
     "corridors": ["Plaza Botero Sculptures", "El Poblado Parque Lleras", "Metrocable Santo Domingo Station", "Avenida El Poblado"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Lima", "country": "Peru", "lat": -12.0464, "lon": -77.0428, "count": 22,
     "corridors": ["Plaza Mayor Palacio de Gobierno", "Miraflores Malecón Larcomar", "Barranco Puente de los Suspiros", "San Isidro Financial District"],
     "stream_url": "https://www.youtube.com/watch?v=6b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Quito", "country": "Ecuador", "lat": -0.1807, "lon": -78.4678, "count": 16,
     "corridors": ["Plaza Grande Palacio Carondelet", "El Panecillo Virgin Vista", "La Mariscal Plaza Foch", "Basílica del Voto Nacional Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Montevideo", "country": "Uruguay", "lat": -34.9011, "lon": -56.1645, "count": 16,
     "corridors": ["Plaza Independencia Palacio Salvo", "Rambla de Montevideo Pocitos", "Ciudad Vieja Peatonal Sarandí", "Port Market Mercado del Puerto"],
     "stream_url": "https://www.youtube.com/watch?v=6b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "La Paz", "country": "Bolivia", "lat": -16.5000, "lon": -68.1500, "count": 14,
     "corridors": ["Plaza Murillo Palacio Quemado", "Mi Teleférico Estación Central", "Sagárnaga Street Witches Market", "Valle de la Luna Vista"],
     "stream_url": "https://www.youtube.com/watch?v=6b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Asunción", "country": "Paraguay", "lat": -25.2637, "lon": -57.5759, "count": 14,
     "corridors": ["Costanera de Asunción Bay", "Palacio de los López Front", "Plaza Uruguaya Central", "Avenida Santa Teresa"],
     "stream_url": "https://www.youtube.com/watch?v=6b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Caracas", "country": "Venezuela", "lat": 10.4806, "lon": -66.9036, "count": 16,
     "corridors": ["Plaza Bolívar Central", "Paseo Los Próceres Boulevard", "Altamira Plaza Francia", "Chacao Avenida Francisco de Miranda"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    # =========================================================================
    # EUROPE: UNITED KINGDOM & IRELAND
    # =========================================================================
    {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278, "count": 35,
     "corridors": ["Abbey Road Crossing", "Tower Bridge North Tower", "Piccadilly Circus LED", "Trafalgar Square Nelson",
                   "Westminster Bridge & Big Ben", "Oxford Street & Regent St", "Covent Garden Market", "St. Paul's Cathedral Plaza",
                   "London Eye South Bank", "Shoreditch High Street", "King's Cross St. Pancras", "Canary Wharf Canada Square"],
     "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo", "stream_type": "youtube"},

    {"city": "Manchester", "country": "UK", "lat": 53.4808, "lon": -2.2426, "count": 16,
     "corridors": ["Piccadilly Gardens", "Deansgate Corridor", "Manchester Arndale Plaza", "Old Trafford Way", "Albert Square Town Hall"],
     "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo", "stream_type": "youtube"},

    {"city": "Birmingham", "country": "UK", "lat": 52.4862, "lon": -1.8904, "count": 16,
     "corridors": ["Bullring Bull Statue", "Centenary Square Library", "New Street Station Ramp", "Victoria Square Council House"],
     "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo", "stream_type": "youtube"},

    {"city": "Edinburgh", "country": "UK", "lat": 55.9533, "lon": -3.1883, "count": 16,
     "corridors": ["Princes Street & Gardens", "Royal Mile High St", "Edinburgh Castle Esplanade", "Calton Hill Overlook", "Grassmarket Historic"],
     "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo", "stream_type": "youtube"},

    {"city": "Glasgow", "country": "UK", "lat": 55.8642, "lon": -4.2518, "count": 14,
     "corridors": ["George Square Chambers", "Buchanan Street Pedestrian", "Merchant City Mercat Cross", "Clyde Arc Squinty Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo", "stream_type": "youtube"},

    {"city": "Belfast", "country": "UK", "lat": 54.5973, "lon": -5.9301, "count": 14,
     "corridors": ["Donegall Square City Hall", "Titanic Quarter Slipways", "Cathedral Quarter Commercial Court", "Queen's University Lanyon"],
     "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo", "stream_type": "youtube"},

    {"city": "Dublin", "country": "Ireland", "lat": 53.3498, "lon": -6.2603, "count": 18,
     "corridors": ["Temple Bar Fleet St", "O'Connell Bridge Liffey", "Grafton Street Pedestrian", "Trinity College Gate", "Custom House Quay", "St. Stephen's Green North"],
     "stream_url": "https://www.youtube.com/watch?v=1b2w1x4e_zL", "stream_type": "youtube"},

    # =========================================================================
    # EUROPE: FRANCE, GERMANY, BENELUX & ALPINE
    # =========================================================================
    {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522, "count": 32,
     "corridors": ["Eiffel Tower & Pont d'Iéna", "Champs-Élysées & Arc de Triomphe", "Louvre Pyramid Courtyard",
                   "Notre-Dame Cathedral Parvis", "Montmartre Sacré-Cœur Steps", "Place de la Concorde",
                   "Opéra Garnier Square", "Pont Neuf & Seine", "Moulin Rouge Blanche", "Boulevard Saint-Germain"],
     "stream_url": "https://www.youtube.com/watch?v=OzYpA4jP1K4", "stream_type": "youtube"},

    {"city": "Marseille", "country": "France", "lat": 43.2965, "lon": 5.3698, "count": 16,
     "corridors": ["Vieux-Port Quai des Belges", "Notre-Dame de la Garde Vista", "La Canebière Central", "MuCEM Promenade Robert Laffont"],
     "stream_url": "https://www.youtube.com/watch?v=OzYpA4jP1K4", "stream_type": "youtube"},

    {"city": "Lyon", "country": "France", "lat": 45.7640, "lon": 4.8357, "count": 16,
     "corridors": ["Place Bellecour Louis XIV", "Fourvière Basilica Esplanade", "Place des Terreaux Bartholdi", "Presqu'île Rue de la République"],
     "stream_url": "https://www.youtube.com/watch?v=OzYpA4jP1K4", "stream_type": "youtube"},

    {"city": "Nice", "country": "France", "lat": 43.7102, "lon": 7.2620, "count": 14,
     "corridors": ["Promenade des Anglais", "Place Masséna Fountain", "Quai des États-Unis", "Port Lympia Entrance"],
     "stream_url": "https://www.youtube.com/watch?v=OzYpA4jP1K4", "stream_type": "youtube"},

    {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050, "count": 26,
     "corridors": ["Brandenburger Tor Pariser Platz", "Alexanderplatz Fernsehturm", "Potsdamer Platz Sony Center",
                   "Checkpoint Charlie Friedrichstraße", "Kurfürstendamm Memorial", "Reichstag Lawn", "Oberbaumbrücke Spree"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Munich", "country": "Germany", "lat": 48.1351, "lon": 11.5820, "count": 20,
     "corridors": ["Marienplatz Neues Rathaus", "Olympiapark Tower Vista", "Karlsplatz Stachus", "Sendlinger Tor", "Odeonsplatz Theatinerkirche"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Frankfurt", "country": "Germany", "lat": 50.1109, "lon": 8.6821, "count": 18,
     "corridors": ["Römerberg Historic Square", "Main River Eisener Steg", "Zeil Shopping Promenade", "Financial District Taunusanlage", "Hauptbahnhof Vorplatz"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Hamburg", "country": "Germany", "lat": 53.5511, "lon": 9.9937, "count": 18,
     "corridors": ["Elbphilharmonie Plaza", "Speicherstadt Wasserschloss", "Jungfernstieg Binnenalster", "St. Pauli Landungsbrücken", "Rathausmarkt"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Cologne", "country": "Germany", "lat": 50.9375, "lon": 6.9603, "count": 16,
     "corridors": ["Kölner Dom Cathedral Forecourt", "Hohenzollernbrücke Rhine Bridge", "Heumarkt Historic", "Neumarkt Shopping Center"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lon": 4.9041, "count": 24,
     "corridors": ["Dam Square & Royal Palace", "Rokin Canal Pier", "Leidseplein Square", "Rembrandtplein", "Centraal Station Front", "Museumplein Rijksmuseum"],
     "stream_url": "https://www.youtube.com/watch?v=f2s2_9yvYh0", "stream_type": "youtube"},

    {"city": "Rotterdam", "country": "Netherlands", "lat": 51.9244, "lon": 4.4777, "count": 16,
     "corridors": ["Erasmusbrug Swan Bridge", "Markthal Binnenrotte", "Cube Houses Overblaak", "Wilhelminapier Kop van Zuid"],
     "stream_url": "https://www.youtube.com/watch?v=f2s2_9yvYh0", "stream_type": "youtube"},

    {"city": "Brussels", "country": "Belgium", "lat": 50.8503, "lon": 4.3517, "count": 18,
     "corridors": ["Grand Place Town Hall", "Place de Brouckère", "Atomium Park Boulevard", "European Parliament Esplanade", "Mont des Arts Vista"],
     "stream_url": "https://www.youtube.com/watch?v=f2s2_9yvYh0", "stream_type": "youtube"},

    {"city": "Zurich", "country": "Switzerland", "lat": 47.3769, "lon": 8.5417, "count": 16,
     "corridors": ["Limmatquai & Grossmünster", "Bahnhofstrasse Central", "Quaibrücke Lake Zurich", "Bürkliplatz Pier"],
     "stream_url": "https://www.youtube.com/watch?v=3b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Geneva", "country": "Switzerland", "lat": 46.2044, "lon": 6.1432, "count": 14,
     "corridors": ["Jet d'Eau Lake Geneva", "Pont du Mont-Blanc", "Place des Nations Palais des Nations", "Vieille Ville Place du Bourg-de-Four"],
     "stream_url": "https://www.youtube.com/watch?v=3b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Vienna", "country": "Austria", "lat": 48.2082, "lon": 16.3738, "count": 20,
     "corridors": ["Stephansplatz St. Stephen's", "Rathausplatz City Hall", "Ringstraße Opera", "Prater Riesenrad Ferris Wheel", "Karlsplatz Karlskirche"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    # =========================================================================
    # EUROPE: MEDITERRANEAN & IBERIA
    # =========================================================================
    {"city": "Rome", "country": "Italy", "lat": 41.9028, "lon": 12.4964, "count": 28,
     "corridors": ["Piazza del Colosseo", "Trevi Fountain Basin", "Piazza di Spagna Spanish Steps", "Piazza Navona Bernini",
                   "Piazza Venezia Altar", "Pantheon Piazza della Rotonda", "Castel Sant'Angelo Bridge", "Vatican St. Peter's View"],
     "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g", "stream_type": "youtube"},

    {"city": "Venice", "country": "Italy", "lat": 45.4408, "lon": 12.3155, "count": 22,
     "corridors": ["Rialto Bridge Grand Canal", "Piazza San Marco Bell Tower", "St. Mark's Basin Waterfront", "Ponte dell'Accademia", "Santa Maria della Salute Pier"],
     "stream_url": "https://www.youtube.com/watch?v=ph1vpnYIxJk", "stream_type": "youtube"},

    {"city": "Florence", "country": "Italy", "lat": 43.7696, "lon": 11.2558, "count": 18,
     "corridors": ["Ponte Vecchio Arno River", "Piazza del Duomo Santa Maria", "Piazza della Signoria", "Piazzale Michelangelo"],
     "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g", "stream_type": "youtube"},

    {"city": "Milan", "country": "Italy", "lat": 45.4642, "lon": 9.1900, "count": 20,
     "corridors": ["Piazza del Duomo Facade", "Galleria Vittorio Emanuele", "Castello Sforzesco Gate", "Navigli Grande Canal", "Piazza Gae Aulenti Skyscraper"],
     "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g", "stream_type": "youtube"},

    {"city": "Naples", "country": "Italy", "lat": 40.8518, "lon": 14.2681, "count": 16,
     "corridors": ["Piazza del Plebiscito", "Castel dell'Ovo Waterfront", "Spaccanapoli Historic Center", "Via Caracciolo Sea Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g", "stream_type": "youtube"},

    {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lon": -3.7038, "count": 25,
     "corridors": ["Puerta del Sol Km 0", "Gran Vía Metropolis", "Plaza Mayor Porticos", "Plaza de Cibeles Fountain",
                   "Puerta de Alcalá", "Plaza de España Cervantes", "Paseo del Prado Museum"],
     "stream_url": "https://www.youtube.com/watch?v=2b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Barcelona", "country": "Spain", "lat": 41.3851, "lon": 2.1734, "count": 25,
     "corridors": ["Sagrada Família Nativity Facade", "La Rambla Canaletes", "Plaça de Catalunya", "Barceloneta Beach Promenade",
                   "Passeig de Gràcia Casa Batlló", "Park Güell Terrace", "Arc de Triomf Passeig de Lluís Companys"],
     "stream_url": "https://www.youtube.com/watch?v=2b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Seville", "country": "Spain", "lat": 37.3891, "lon": -5.9845, "count": 16,
     "corridors": ["Plaza de España Arcades", "La Giralda Cathedral Square", "Torre del Oro Guadalquivir River", "Triana Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=2b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Valencia", "country": "Spain", "lat": 39.4699, "lon": -0.3763, "count": 16,
     "corridors": ["Ciutat de les Arts i les Ciències", "Plaza del Ayuntamiento", "Torres de Serranos", "Playa de la Malvarrosa Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=2b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Lisbon", "country": "Portugal", "lat": 38.7223, "lon": -9.1393, "count": 20,
     "corridors": ["Praça do Comércio Tagus View", "Rossio Square Fountains", "Belém Tower Waterfront", "Santa Justa Lift Plaza", "Miradouro de Santa Luzia"],
     "stream_url": "https://www.youtube.com/watch?v=2b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Porto", "country": "Portugal", "lat": 41.1579, "lon": -8.6291, "count": 16,
     "corridors": ["Dom Luís I Bridge Douro", "Ribeira Waterfront Promenade", "Avenida dos Aliados City Hall", "Clérigos Tower Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=2b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Athens", "country": "Greece", "lat": 37.9838, "lon": 23.7275, "count": 22,
     "corridors": ["Acropolis & Parthenon Panorama", "Syntagma Square Parliament", "Monastiraki Flea Market Square", "Plaka Old Town", "Panathenaic Stadium"],
     "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g", "stream_type": "youtube"},

    {"city": "Thessaloniki", "country": "Greece", "lat": 40.6401, "lon": 22.9444, "count": 14,
     "corridors": ["White Tower Waterfront Promenade", "Aristotelous Square Sea View", "Ano Poli Old Town Walls", "Arch of Galerius Egnatia"],
     "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g", "stream_type": "youtube"},

    # =========================================================================
    # EUROPE: NORDICS, BALTICS & EASTERN EUROPE
    # =========================================================================
    {"city": "Stockholm", "country": "Sweden", "lat": 59.3293, "lon": 18.0686, "count": 18,
     "corridors": ["Gamla Stan Royal Palace", "Sergels Torg Square", "Slussen Harbor Lock", "Kungsträdgården Park", "Djurgården Ferry Slip"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Oslo", "country": "Norway", "lat": 59.9139, "lon": 10.7522, "count": 16,
     "corridors": ["Karl Johans Gate Parliament", "Aker Brygge Waterfront", "Oslo Opera House Roof", "Vigeland Park Monolith", "Holmenkollen Ski Jump"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Copenhagen", "country": "Denmark", "lat": 55.6761, "lon": 12.5683, "count": 18,
     "corridors": ["Nyhavn Colorful Waterfront", "Rådhuspladsen City Hall", "Strøget Walking Street", "Amalienborg Palace Square", "The Little Mermaid Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Helsinki", "country": "Finland", "lat": 60.1699, "lon": 24.9384, "count": 16,
     "corridors": ["Senate Square Cathedral", "Market Square Harbor", "Mannerheimintie Central", "Kamppi Narinkkatori", "Esplanadi Park Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Reykjavik", "country": "Iceland", "lat": 64.1466, "lon": -21.9426, "count": 14,
     "corridors": ["Hallgrímskirkja Church Square", "Laugavegur Shopping Street", "Harpa Concert Hall Waterfront", "Old Harbour Marina"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Warsaw", "country": "Poland", "lat": 52.2297, "lon": 21.0122, "count": 22,
     "corridors": ["Old Town Market Square", "Palace of Culture & Science Defilad", "Krakowskie Przedmieście Royal Way", "Nowy Świat Commercial", "Vistula River Boulevards"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Krakow", "country": "Poland", "lat": 50.0647, "lon": 19.9450, "count": 18,
     "corridors": ["Rynek Główny Cloth Hall", "Wawel Royal Castle Vistula", "Kazimierz Plac Nowy", "Floriańska Street Gate"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Prague", "country": "Czechia", "lat": 50.0755, "lon": 14.4378, "count": 22,
     "corridors": ["Old Town Square Astronomical Clock", "Charles Bridge Tower", "Wenceslas Square St. Wenceslas", "Prague Castle Hradcany", "Náměstí Republiky"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Budapest", "country": "Hungary", "lat": 47.4979, "lon": 19.0402, "count": 22,
     "corridors": ["Chain Bridge Danube River", "Hungarian Parliament Kossuth Sq", "Buda Castle Fisherman's Bastion", "Heroes' Square Andrássy Avenue", "St. Stephen's Basilica"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Bucharest", "country": "Romania", "lat": 44.4268, "lon": 26.1025, "count": 18,
     "corridors": ["Palace of the Parliament Constitution Sq", "Piața Unirii Fountains", "Calea Victoriei Historic", "Old Town Lipscani"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Sofia", "country": "Bulgaria", "lat": 42.6977, "lon": 23.3219, "count": 16,
     "corridors": ["Alexander Nevsky Cathedral Square", "Vitosha Boulevard Pedestrian", "Serdika Ancient Complex", "Largo Government Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Zagreb", "country": "Croatia", "lat": 45.8150, "lon": 15.9819, "count": 16,
     "corridors": ["Ban Jelačić Square", "St. Mark's Square Upper Town", "Tkalčićeva Street", "Zagreb Cathedral Kaptol"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Dubrovnik", "country": "Croatia", "lat": 42.6507, "lon": 18.0944, "count": 14,
     "corridors": ["Stradun Placa Main Street", "Pile Gate Old City Entrance", "Old Port Waterfront", "Lovrijenac Fort Vista"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Belgrade", "country": "Serbia", "lat": 44.7866, "lon": 20.4489, "count": 16,
     "corridors": ["Knez Mihailova Pedestrian", "Kalemegdan Fortress Danube Confluence", "Republic Square National Museum", "Saint Sava Temple Vračar"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Kyiv", "country": "Ukraine", "lat": 50.4501, "lon": 30.5234, "count": 22,
     "corridors": ["Maidan Nezalezhnosti Independence Sq", "Khreshchatyk Boulevard", "Saint Sophia Cathedral Plaza", "Kyiv Pechersk Lavra View", "Podil Poshtova Square"],
     "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls", "stream_type": "youtube"},

    {"city": "Tallinn", "country": "Estonia", "lat": 59.4370, "lon": 24.7536, "count": 14,
     "corridors": ["Raekoja Plats Town Hall", "Toompea Hill Alexander Nevsky", "Viru Gate Old Town Entrance", "Port of Tallinn Cruise Pier"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Riga", "country": "Latvia", "lat": 56.9496, "lon": 24.1052, "count": 14,
     "corridors": ["House of the Black Heads Town Hall", "Freedom Monument Boulevard", "Dome Square Old Riga", "Daugava Stone Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    {"city": "Vilnius", "country": "Lithuania", "lat": 54.6872, "lon": 25.2797, "count": 14,
     "corridors": ["Cathedral Square Bell Tower", "Gediminas Tower Hilltop", "Gedimino Avenue Commercial", "Užupis Angel Square"],
     "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A", "stream_type": "youtube"},

    # =========================================================================
    # MIDDLE EAST & NORTH AFRICA
    # =========================================================================
    {"city": "Istanbul", "country": "Turkey", "lat": 41.0082, "lon": 28.9784, "count": 26,
     "corridors": ["Bosphorus Bridge Strait", "Taksim Square Monument", "Sultanahmet Blue Mosque Plaza", "Galata Tower Vista",
                   "Eminönü Golden Horn Ferry Dock", "İstiklal Avenue Tramway", "Kadıköy Bull Statue Asian Side"],
     "stream_url": "https://www.youtube.com/watch?v=9p3w2y1x4E8", "stream_type": "youtube"},

    {"city": "Ankara", "country": "Turkey", "lat": 39.9334, "lon": 32.8597, "count": 16,
     "corridors": ["Kızılay Square Central", "Anıtkabir Atatürk Mausoleum Plaza", "Ulus Square Republic Monument", "Atakule Tower Vista"],
     "stream_url": "https://www.youtube.com/watch?v=9p3w2y1x4E8", "stream_type": "youtube"},

    {"city": "Dubai", "country": "UAE", "lat": 25.2048, "lon": 55.2708, "count": 28,
     "corridors": ["Marina Walk & Yacht Club", "Burj Khalifa Downtown Promenade", "Sheikh Zayed Road Skyway", "Palm Jumeirah Atlantis",
                   "Dubai Mall Waterfront Fountain", "Deira Gold Souk Creek", "JBR The Beach Walk", "Dubai Canal Waterfall Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Abu Dhabi", "country": "UAE", "lat": 24.4539, "lon": 54.3773, "count": 18,
     "corridors": ["Corniche Beach Promenade", "Sheikh Zayed Grand Mosque Entrance", "Yas Marina Circuit", "Louvre Abu Dhabi Plaza", "Emirates Palace Boulevard"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Riyadh", "country": "Saudi Arabia", "lat": 24.7136, "lon": 46.6753, "count": 22,
     "corridors": ["Kingdom Centre Sky Bridge", "Al Faisaliah Tower Plaza", "King Fahd Road Highway", "Boulevard Riyadh City", "Diriyah Historical Gateway"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Jeddah", "country": "Saudi Arabia", "lat": 21.5433, "lon": 39.1728, "count": 18,
     "corridors": ["Jeddah Corniche Red Sea", "King Fahd Fountain", "Al-Balad Historic Gate", "North Corniche Floating Mosque"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Mecca", "country": "Saudi Arabia", "lat": 21.3891, "lon": 39.8579, "count": 20,
     "corridors": ["Masjid al-Haram Courtyard", "Abraj Al-Bait Clock Tower", "Jabal al-Nour Overlook", "Ibrahim Al Khalil Road"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Medina", "country": "Saudi Arabia", "lat": 24.5247, "lon": 39.5692, "count": 18,
     "corridors": ["Al-Masjid an-Nabawi Green Dome", "King Fahd Central Ring Road", "Quba Mosque Courtyard", "Mount Uhud Memorial Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Doha", "country": "Qatar", "lat": 25.2854, "lon": 51.5310, "count": 18,
     "corridors": ["Doha Corniche Waterfront", "Souq Waqif Main Square", "The Pearl Porto Arabia", "Katara Cultural Village", "Lusail Marina Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Kuwait City", "country": "Kuwait", "lat": 29.3759, "lon": 47.9774, "count": 16,
     "corridors": ["Kuwait Towers Seaside", "Arabian Gulf Street", "Souk Al-Mubarakiya", "Al Shaheed Park Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Manama", "country": "Bahrain", "lat": 26.2285, "lon": 50.5860, "count": 14,
     "corridors": ["Bahrain World Trade Center", "Bab Al Bahrain Manama Souq", "King Fahd Causeway Gateway", "Bahrain Bay Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Muscat", "country": "Oman", "lat": 23.5880, "lon": 58.3829, "count": 16,
     "corridors": ["Muttrah Corniche & Souq", "Sultan Qaboos Grand Mosque", "Al Alam Palace Gate", "Riyam Park Incense Burner Vista"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lon": 34.7818, "count": 18,
     "corridors": ["Herbert Samuel Promenade Beach", "Rothschild Boulevard", "Dizengoff Square Fountain", "Old Jaffa Port Harbour", "Ayalon Highway Corridor"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Jerusalem", "country": "Israel", "lat": 31.7683, "lon": 35.2137, "count": 18,
     "corridors": ["Western Wall Plaza", "Jaffa Gate Old City", "Mount of Olives Panorama", "Machane Yehuda Market", "Mamilla Mall Avenue"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Amman", "country": "Jordan", "lat": 31.9454, "lon": 35.9284, "count": 16,
     "corridors": ["Amman Citadel Temple of Hercules", "Roman Theatre Plaza", "Rainbow Street Jabal Amman", "Downtown Al-Balad King Faisal St"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Beirut", "country": "Lebanon", "lat": 33.8938, "lon": 35.5018, "count": 16,
     "corridors": ["Beirut Corniche Raouche Rocks", "Nejmeh Square Parliament", "Zaitunay Bay Yacht Club", "Hamra Street Commercial"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Baghdad", "country": "Iraq", "lat": 33.3152, "lon": 44.3661, "count": 16,
     "corridors": ["Tahrir Square Liberation Monument", "Firdos Square Corridor", "Al-Mutanabbi Street Book Market", "Tigris River Corniche"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Tehran", "country": "Iran", "lat": 35.6892, "lon": 51.3890, "count": 18,
     "corridors": ["Azadi Tower Square", "Milad Tower Vista", "Valiasr Street Boulevard", "Tajrish Square Grand Bazaar"],
     "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E", "stream_type": "youtube"},

    {"city": "Cairo", "country": "Egypt", "lat": 30.0444, "lon": 31.2357, "count": 22,
     "corridors": ["Giza Plateau & Great Pyramids", "Tahrir Square Central", "Nile Corniche Promenade", "Khan el-Khalili Bazaar",
                   "Cairo Tower Gezira Island", "6th October Bridge Flyover"],
     "stream_url": "https://www.youtube.com/watch?v=1x2w4e_zK1s", "stream_type": "youtube"},

    {"city": "Alexandria", "country": "Egypt", "lat": 31.2001, "lon": 29.9187, "count": 16,
     "corridors": ["Corniche Mediterranean Seafront", "Citadel of Qaitbay Promontory", "Bibliotheca Alexandrina Plaza", "Stanley Bridge Crossing"],
     "stream_url": "https://www.youtube.com/watch?v=1x2w4e_zK1s", "stream_type": "youtube"},

    {"city": "Casablanca", "country": "Morocco", "lat": 33.5731, "lon": -7.5898, "count": 18,
     "corridors": ["Hassan II Mosque Corniche", "Place des Nations Unies", "Ain Diab Beach Walkway", "Boulevard d'Anfa", "Old Medina Bab Marrakesh"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Marrakech", "country": "Morocco", "lat": 31.6295, "lon": -7.9811, "count": 16,
     "corridors": ["Jemaa el-Fnaa Main Square", "Koutoubia Mosque Gardens", "Avenue Mohammed VI Gueliz", "Bab Agnaou Historic Gate"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Algiers", "country": "Algeria", "lat": 36.7538, "lon": 3.0588, "count": 16,
     "corridors": ["Martyrs' Memorial Maqam Echahid", "Casbah of Algiers Port", "Didouche Mourad Commercial", "Place des Martyrs Central"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Tunis", "country": "Tunisia", "lat": 36.8065, "lon": 10.1815, "count": 14,
     "corridors": ["Avenue Habib Bourguiba Clock Tower", "Medina of Tunis Bab El Bhar", "Carthage Byrsa Hill Vista", "Sidi Bou Said Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=5b2w1x4e_zL", "stream_type": "youtube"},

    # =========================================================================
    # SUB-SAHARAN AFRICA
    # =========================================================================
    {"city": "Cape Town", "country": "South Africa", "lat": -33.9249, "lon": 18.4241, "count": 22,
     "corridors": ["V&A Waterfront Clock Tower", "Table Mountain Cableway Lower", "Camps Bay Beach Promenade", "Kirstenbosch Gardens Gate",
                   "Boulders Beach Penguin Colony", "Signal Hill Paragliding Launch", "Long Street Heritage"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Johannesburg", "country": "South Africa", "lat": -26.2041, "lon": 28.0473, "count": 18,
     "corridors": ["Nelson Mandela Square Sandton", "Maboneng Precinct Fox St", "Rosebank Commercial Hub", "Braamfontein Bridge", "Constitutional Hill Gate"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Durban", "country": "South Africa", "lat": -29.8587, "lon": 31.0218, "count": 16,
     "corridors": ["Golden Mile Beachfront Promenade", "Moses Mabhida Stadium Arch", "uShaka Marine World", "Florida Road Entertainment"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Nairobi", "country": "Kenya", "lat": -1.2921, "lon": 36.8219, "count": 18,
     "corridors": ["Kenyatta Avenue Central", "Uhuru Park Memorial", "Nairobi Expressway Westlands", "Upper Hill Financial Hub", "Moi Avenue CBD"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Lagos", "country": "Nigeria", "lat": 6.5244, "lon": 3.3792, "count": 22,
     "corridors": ["Lekki-Ikoyi Link Bridge", "Victoria Island Adeola Odeku", "Marina CMS Ferry Terminal", "Tafawa Balewa Square", "Third Mainland Bridge Approach"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Abuja", "country": "Nigeria", "lat": 9.0765, "lon": 7.3986, "count": 16,
     "corridors": ["National Mosque Abuja", "Aso Rock Presidential Way", "Millennium Park Promenade", "Central Business District Shehu Shagari Way"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Accra", "country": "Ghana", "lat": 5.6037, "lon": -0.1870, "count": 16,
     "corridors": ["Black Star Square Independence Arch", "Osu Oxford Street", "Jamestown Lighthouse Fishery", "Kotoka Airport Bypass"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Addis Ababa", "country": "Ethiopia", "lat": 9.0320, "lon": 38.7469, "count": 16,
     "corridors": ["Meskel Square Central", "Bole Road Africa Avenue", "Piazza Churchill Avenue", "AU Headquarters Roosevelt St"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Dar es Salaam", "country": "Tanzania", "lat": -6.7924, "lon": 39.2083, "count": 16,
     "corridors": ["Kigamboni Bridge Nyerere", "Kivukoni Fish Market Ferry", "Askari Monument Samora Ave", "Coco Beach Seafront"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Kampala", "country": "Uganda", "lat": 0.3476, "lon": 32.5825, "count": 14,
     "corridors": ["Kampala Road CBD", "Old Kampala Mosque Hill", "Kololo Independence Grounds", "Entebbe Expressway Interchange"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Kigali", "country": "Rwanda", "lat": -1.9441, "lon": 30.0619, "count": 14,
     "corridors": ["Kigali Convention Centre Roundabout", "KG 1 Roundabout Downtown", "Nyarutarama Golf View", "Remera Stadium Corridor"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    {"city": "Dakar", "country": "Senegal", "lat": 14.7167, "lon": -17.4677, "count": 14,
     "corridors": ["African Renaissance Monument", "Place de l'Indépendance", "Corniche Ouest Seafront", "Goreé Island Ferry Pier"],
     "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL", "stream_type": "youtube"},

    # =========================================================================
    # SOUTH ASIA
    # =========================================================================
    {"city": "Mumbai", "country": "India", "lat": 19.0760, "lon": 72.8777, "count": 28,
     "corridors": ["Marine Drive Queen's Necklace", "Gateway of India Colaba", "Bandra-Worli Sea Link Toll", "Chhatrapati Shivaji Terminus",
                   "Juhu Beach Promenade", "Nariman Point Financial Center", "Bandra Carter Road", "Andheri Western Express Highway", "Dadar TT Circle"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Delhi", "country": "India", "lat": 28.7041, "lon": 77.1025, "count": 26,
     "corridors": ["India Gate Rajpath", "Connaught Place Inner Circle", "Chandni Chowk Red Fort", "Qutub Minar Complex",
                   "Cyber City Gurugram Corridor", "Ring Road AIIMS Crossing", "Noida Expressway Toll Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Bengaluru", "country": "India", "lat": 12.9716, "lon": 77.5946, "count": 22,
     "corridors": ["MG Road Metro Station", "Brigade Road Commercial", "Electronic City Flyover", "Whitefield ITPL Main Rd", "Vidhana Soudha", "Silk Board Junction"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Hyderabad", "country": "India", "lat": 17.3850, "lon": 78.4867, "count": 20,
     "corridors": ["Charminar Historic Plaza", "HITEC City Cyber Towers", "Hussain Sagar Lake Buddha Statue", "Gachibowli Outer Ring Road", "Banjara Hills Road 1"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Chennai", "country": "India", "lat": 13.0827, "lon": 80.2707, "count": 20,
     "corridors": ["Marina Beach Lighthouse Promenade", "OMR IT Corridor Tidel Park", "Anna Salai Mount Road", "Kathipara Flyover Cloverleaf", "Central Station Forecourt"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Kolkata", "country": "India", "lat": 22.5726, "lon": 88.3639, "count": 20,
     "corridors": ["Howrah Bridge Hooghly River", "Victoria Memorial North Gate", "Park Street Commercial", "Vidyasagar Setu Toll Plaza", "Salt Lake Sector V"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Pune", "country": "India", "lat": 18.5204, "lon": 73.8567, "count": 16,
     "corridors": ["FC Road Commercial Belt", "Hinjawadi IT Park Phase 1", "Shaniwar Wada Historic Gate", "Koregaon Park North Main Rd"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Ahmedabad", "country": "India", "lat": 23.0225, "lon": 72.5714, "count": 16,
     "corridors": ["Sabarmati Riverfront Promenade", "SG Highway Corporate Corridor", "Atal Pedestrian Bridge", "Kankaria Lake Gate"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Jaipur", "country": "India", "lat": 26.9124, "lon": 75.7873, "count": 16,
     "corridors": ["Hawa Mahal Palace of Winds", "Jal Mahal Man Sagar Lake", "Amer Fort Ascending Ramp", "MI Road Ajmeri Gate"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Kochi", "country": "India", "lat": 9.9312, "lon": 76.2673, "count": 16,
     "corridors": ["Marine Drive Walkway Rainbow Bridge", "Fort Kochi Chinese Fishing Nets", "MG Road Ernakulam", "Vallarpadam Container Terminal Road"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Karachi", "country": "Pakistan", "lat": 24.8607, "lon": 67.0011, "count": 20,
     "corridors": ["Clifton Sea View Beach", "Mazar-e-Quaid Mausoleum", "Shahrah-e-Faisal Corporate", "Port Grand Waterfront"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Lahore", "country": "Pakistan", "lat": 31.5204, "lon": 74.3587, "count": 18,
     "corridors": ["Badshahi Mosque Hazuri Bagh", "Minar-e-Pakistan Greater Iqbal Park", "Mall Road Commercial", "Liberty Roundabout Gulberg"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Islamabad", "country": "Pakistan", "lat": 33.6844, "lon": 73.0479, "count": 16,
     "corridors": ["Faisal Mosque Courtyard", "Daman-e-Koh Margalla Hills", "Constitution Avenue Parliament", "Blue Area Jinnah Avenue"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Dhaka", "country": "Bangladesh", "lat": 23.8103, "lon": 90.4125, "count": 20,
     "corridors": ["Jatiya Sangsad Bhaban Parliament", "Hatirjheel Lake Express Bridge", "Gulshan 2 Circle", "Shahbagh Intersection"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Colombo", "country": "Sri Lanka", "lat": 6.9271, "lon": 79.8612, "count": 16,
     "corridors": ["Galle Face Green Promenade", "Lotus Tower Skybridge", "Pettah Floating Market", "Colombo Port City Causeway"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    {"city": "Kathmandu", "country": "Nepal", "lat": 27.7172, "lon": 85.3240, "count": 16,
     "corridors": ["Kathmandu Durbar Square", "Boudhanath Stupa Circle", "Swayambhunath Monkey Temple Hill", "Thamel Mandala Street"],
     "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A", "stream_type": "youtube"},

    # =========================================================================
    # EAST ASIA: JAPAN, SOUTH KOREA, TAIWAN & GREATER CHINA
    # =========================================================================
    {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "count": 40,
     "corridors": ["Shibuya Scramble Crossing", "Shinjuku Kabukicho East", "Akihabara Chuo Dori", "Ginza 4-Chome Wako",
                   "Roppongi Hills Mori Tower", "Tokyo Tower Foot Town", "Asakusa Kaminarimon Sensoji", "Odaiba Rainbow Bridge",
                   "Haneda Airport Runway View", "Ikebukuro East Exit", "Ueno Station Ameyoko", "Nihombashi Historic Bridge",
                   "Yurakucho Elevated Tracks", "Harajuku Takeshita St", "Tokyo Skytree Town"],
     "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y", "stream_type": "youtube"},

    {"city": "Osaka", "country": "Japan", "lat": 34.6937, "lon": 135.5023, "count": 24,
     "corridors": ["Dotonbori Glico Running Man", "Shinsaibashi Shopping Arcade", "Osaka Castle Park", "Umeda Sky Building Vista",
                   "Tsutenkaku Shinsekai Tower", "Namba Station Intersection", "Midosuji Boulevard"],
     "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y", "stream_type": "youtube"},

    {"city": "Kyoto", "country": "Japan", "lat": 35.0116, "lon": 135.7681, "count": 18,
     "corridors": ["Gion Shijo Dori Geisha Quarter", "Kyoto Station Karasuma Plaza", "Kiyomizu-dera Approaching Slope", "Kawaramachi Sanjo", "Arashiyama Togetsukyo Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y", "stream_type": "youtube"},

    {"city": "Nagoya", "country": "Japan", "lat": 35.1815, "lon": 136.9066, "count": 18,
     "corridors": ["Nagoya Station Twin Towers Plaza", "Sakae TV Tower Oasis 21", "Nagoya Castle Main Gate", "Osu Kannon Shopping Arcade"],
     "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y", "stream_type": "youtube"},

    {"city": "Fukuoka", "country": "Japan", "lat": 33.5904, "lon": 130.4017, "count": 16,
     "corridors": ["Tenjin Crossing Crossing", "Hakata Station Hakata-guchi", "Nakasu Island Yatai Stalls", "Fukuoka Tower Momochi Seaside"],
     "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y", "stream_type": "youtube"},

    {"city": "Sapporo", "country": "Japan", "lat": 43.0618, "lon": 141.3545, "count": 16,
     "corridors": ["Odori Park TV Tower", "Susukino Nikka Sign Crossing", "Sapporo Clock Tower", "JR Tower Station Front Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y", "stream_type": "youtube"},

    {"city": "Seoul", "country": "South Korea", "lat": 37.5665, "lon": 126.9780, "count": 32,
     "corridors": ["Gangnam-daero Center", "Myeongdong Shopping Street", "Gwanghwamun Square King Sejong", "Hongdae University Street",
                   "Namsan Tower Seoul Skyline", "Yeouido Financial District", "Itaewon World Street", "Dongdaemun DDP Plaza",
                   "Han River Banpo Bridge", "Jamsil Lotte World Tower", "COEX Starfield Atrium"],
     "stream_url": "https://www.youtube.com/watch?v=3g_2d6gE1P8", "stream_type": "youtube"},

    {"city": "Busan", "country": "South Korea", "lat": 35.1796, "lon": 129.0756, "count": 18,
     "corridors": ["Haeundae Beach Boardwalk", "Gwangalli Gwangan Diamond Bridge", "Jagalchi Fish Market Pier", "Seomyeon Medical Center", "Busan Station Plaza"],
     "stream_url": "https://www.youtube.com/watch?v=3g_2d6gE1P8", "stream_type": "youtube"},

    {"city": "Incheon", "country": "South Korea", "lat": 37.4563, "lon": 126.7052, "count": 16,
     "corridors": ["Songdo Central Park Waterway", "Incheon Bridge Cable-Stayed Span", "Chinatown Paeru Gate", "Wolmido Island Seafront"],
     "stream_url": "https://www.youtube.com/watch?v=3g_2d6gE1P8", "stream_type": "youtube"},

    {"city": "Taipei", "country": "Taiwan", "lat": 25.0330, "lon": 121.5654, "count": 22,
     "corridors": ["Taipei 101 Xinyi District", "Ximending Pedestrian Zone", "Shilin Night Market", "Chiang Kai-shek Memorial Square",
                   "Zhongxiao East Road", "Keelung River Dazhi Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Kaohsiung", "country": "Taiwan", "lat": 22.6273, "lon": 120.3014, "count": 16,
     "corridors": ["Love River Promenade", "Pier-2 Art Center Waterfront", "85 Sky Tower Tuntex", "Formosa Boulevard Dome of Light"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Hong Kong", "country": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "count": 28,
     "corridors": ["Victoria Harbour Tsim Sha Tsui", "Central Star Ferry Pier", "Mong Kok Nathan Road", "Causeway Bay Sogo Crossing",
                   "Peak Tram Sky Terrace", "Wan Chai Convention Centre", "Aberdeen Typhoon Shelter", "Lan Kwai Fong Pedestrian", "Tsing Ma Bridge"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Macau", "country": "Macau", "lat": 22.1987, "lon": 113.5439, "count": 16,
     "corridors": ["Ruins of St. Paul's Steps", "Senado Square Wave Pavement", "Cotai Strip Venetian Promenade", "Macau Tower Bungy Vista"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Shanghai", "country": "China", "lat": 31.2304, "lon": 121.4737, "count": 30,
     "corridors": ["The Bund Promenade & Huangpu River", "Lujiazui Oriental Pearl Tower", "Nanjing Road Pedestrian Mall", "Yu Garden Old Town",
                   "Xintiandi Shikumen Plaza", "People's Square Government Front", "Jing'an Temple West Nanjing Rd"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Beijing", "country": "China", "lat": 39.9042, "lon": 116.4074, "count": 30,
     "corridors": ["Tiananmen Square South Gate", "Forbidden City Meridian Gate", "Wangfujing Commercial Street", "Sanlitun Taikoo Li",
                   "Olympic Park Bird's Nest", "CBD Guomao China Zun Tower", "Zhongguancun High-Tech Corridor"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Guangzhou", "country": "China", "lat": 23.1291, "lon": 113.2644, "count": 22,
     "corridors": ["Canton Tower Pearl River Bank", "Zhujiang New Town Huacheng Square", "Beijing Road Pedestrian Mall", "Shamian Island European Colonial"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    {"city": "Shenzhen", "country": "China", "lat": 22.5431, "lon": 114.0579, "count": 22,
     "corridors": ["Ping An Finance Centre Plaza", "Civic Center South Square", "Huaqiangbei Electronics Market", "Shenzhen Bay Park Coastal Walk"],
     "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4", "stream_type": "youtube"},

    # =========================================================================
    # SOUTHEAST ASIA
    # =========================================================================
    {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "count": 28,
     "corridors": ["Marina Bay Sands Promenade", "Merlion Park Singapore River", "Orchard Road Shopping Belt", "Changi Airport Jewel",
                   "Sentosa Boardwalk Resort", "Clarke Quay Nightlife", "Raffles Place Financial Heart", "Sheares Bridge Expressway"],
     "stream_url": "https://www.youtube.com/watch?v=r0wO_4X9Nq8", "stream_type": "youtube"},

    {"city": "Bangkok", "country": "Thailand", "lat": 13.7563, "lon": 100.5018, "count": 26,
     "corridors": ["Sukhumvit Nana Intersection", "Siam Paragon SkyTrain Walkway", "Asok Montri Intersection", "Chao Phraya River IconSiam",
                   "Khao San Road", "Silom Patpong Crossing", "Victory Monument Roundabout", "Chinatown Yaowarat Road"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Chiang Mai", "country": "Thailand", "lat": 18.7883, "lon": 98.9853, "count": 16,
     "corridors": ["Tha Phae Gate Old City Moat", "Nimmanahaeminda Road Trendy", "Wat Phra Singh Temple Gate", "Night Bazaar Chang Khlan"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Phuket", "country": "Thailand", "lat": 7.8804, "lon": 98.3923, "count": 16,
     "corridors": ["Patong Beach Bangla Walking St", "Phuket Old Town Thalang Rd", "Promthep Cape Sunset Viewpoint", "Karon Beach Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Kuala Lumpur", "country": "Malaysia", "lat": 3.1390, "lon": 101.6869, "count": 22,
     "corridors": ["Petronas Twin Towers KLCC Park", "Bukit Bintang Pavilion Crossing", "Merdeka 118 Spire View", "Jalan Alor Night Market", "Dataran Merdeka Sultan Abdul Samad"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "George Town", "country": "Malaysia", "lat": 5.4141, "lon": 100.3288, "count": 14,
     "corridors": ["Armenian Street Heritage Murals", "Gurney Drive Seafront Promenade", "KOMTAR Tower Central", "Chulia Street Hawker Stalls"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Jakarta", "country": "Indonesia", "lat": -6.2088, "lon": 106.8456, "count": 24,
     "corridors": ["Bundaran HI Welcome Monument", "Monas National Monument Park", "Sudirman Central Business District", "Kota Tua Fatahillah Square", "Gelora Bung Karno Stadium Gate"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Bali (Denpasar)", "country": "Indonesia", "lat": -8.6705, "lon": 115.2126, "count": 20,
     "corridors": ["Kuta Beach Boardwalk", "Seminyak Kayu Aya Street", "Sanur Beachfront Cycle Path", "Ubud Monkey Forest Main Road", "Canggu Batu Bolong Beach"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Manila", "country": "Philippines", "lat": 14.5995, "lon": 120.9842, "count": 24,
     "corridors": ["Rizal Park Luneta Monument", "Intramuros General Luna St", "Roxas Boulevard Manila Bay Walk", "Binondo Chinatown Arch", "Bonifacio Global City High Street"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Cebu City", "country": "Philippines", "lat": 10.3157, "lon": 123.8854, "count": 16,
     "corridors": ["Fuente Osmeña Circle", "Cebu IT Park Inez Villa", "Magellan's Cross Plaza", "Colon Street Historic"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Ho Chi Minh City", "country": "Vietnam", "lat": 10.8231, "lon": 106.6297, "count": 22,
     "corridors": ["Nguyen Hue Walking Street City Hall", "Ben Thanh Market Clock Tower", "Notre-Dame Cathedral Basilica", "Bui Vien Walking Street", "Landmark 81 Saigon River"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Hanoi", "country": "Vietnam", "lat": 21.0285, "lon": 105.8542, "count": 20,
     "corridors": ["Hoan Kiem Lake Turtle Tower", "Hanoi Opera House Plaza", "Old Quarter Ta Hien Beer Street", "Ba Dinh Square Ho Chi Minh Mausoleum"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Da Nang", "country": "Vietnam", "lat": 16.0544, "lon": 108.2022, "count": 16,
     "corridors": ["Dragon Bridge Han River", "My Khe Beach Vo Nguyen Giap", "Han Market Bach Dang St", "Golden Bridge Ba Na Hills"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Phnom Penh", "country": "Cambodia", "lat": 11.5564, "lon": 104.9282, "count": 16,
     "corridors": ["Royal Palace Tonle Sap Riverfront", "Independence Monument Roundabout", "Wat Phnom Historical Hill", "Central Market Phsar Thmey"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    {"city": "Yangon", "country": "Myanmar", "lat": 16.8661, "lon": 96.1951, "count": 14,
     "corridors": ["Shwedagon Pagoda East Stairway", "Sule Pagoda Downtown Intersection", "Kandawgyi Lake Boardwalk", "Strand Road Port"],
     "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E", "stream_type": "youtube"},

    # =========================================================================
    # OCEANIA: AUSTRALIA, NEW ZEALAND & PACIFIC
    # =========================================================================
    {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "count": 28,
     "corridors": ["Circular Quay & Harbour Bridge", "Sydney Opera House Forecourt", "Bondi Beach Pavilion", "Manly Beach Corso",
                   "Darling Harbour Cockle Bay", "George Street Light Rail", "Anzac Bridge Highway", "Coogee Beach Coastal"],
     "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM", "stream_type": "youtube"},

    {"city": "Melbourne", "country": "Australia", "lat": -37.8136, "lon": 144.9631, "count": 24,
     "corridors": ["Flinders Street Station Plaza", "Federation Square", "Bourke Street Mall", "Southbank Yarra River Promenade",
                   "St Kilda Pier & Beach", "Docklands Marina Harbour", "Lygon Street Carlton"],
     "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM", "stream_type": "youtube"},

    {"city": "Brisbane", "country": "Australia", "lat": -27.4698, "lon": 153.0251, "count": 18,
     "corridors": ["South Bank Parklands Lagoon", "Story Bridge River View", "Queen Street Mall", "Eagle Street Pier", "Howard Smith Wharves"],
     "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM", "stream_type": "youtube"},

    {"city": "Perth", "country": "Australia", "lat": -31.9505, "lon": 115.8605, "count": 18,
     "corridors": ["Elizabeth Quay Swan River", "Kings Park War Memorial Vista", "Hay Street Mall", "Cottesloe Beach Pylon", "Fremantle Fishing Boat Harbour"],
     "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM", "stream_type": "youtube"},

    {"city": "Adelaide", "country": "Australia", "lat": -34.9285, "lon": 138.6007, "count": 16,
     "corridors": ["Rundle Mall Bronze Pigs", "Adelaide Oval Torrens Riverbank", "Victoria Square Tarntanyangga", "Glenelg Moseley Square Pier"],
     "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM", "stream_type": "youtube"},

    {"city": "Gold Coast", "country": "Australia", "lat": -28.0167, "lon": 153.4000, "count": 16,
     "corridors": ["Surfers Paradise Cavill Avenue", "Broadbeach Kurrawa Park", "Q1 SkyPoint Observation Deck", "Burleigh Heads Point Break"],
     "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM", "stream_type": "youtube"},

    {"city": "Auckland", "country": "New Zealand", "lat": -36.8485, "lon": 174.7633, "count": 20,
     "corridors": ["Queen Street Wharf", "Sky Tower Plaza", "Viaduct Harbour Marina", "Auckland Harbour Bridge Approach", "Mission Bay Beach Promenade"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zM", "stream_type": "youtube"},

    {"city": "Wellington", "country": "New Zealand", "lat": -41.2865, "lon": 174.7762, "count": 16,
     "corridors": ["Lambton Quay Golden Mile", "Wellington Cable Car Kelburn Terminus", "Oriental Bay Beachfront", "Parliament Beehive Forecourt"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zM", "stream_type": "youtube"},

    {"city": "Christchurch", "country": "New Zealand", "lat": -43.5321, "lon": 172.6362, "count": 16,
     "corridors": ["Cathedral Square Transition Cathedral", "New Regent Street Tramway", "Avon River Terraces", "Bridge of Remembrance Cashel St"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zM", "stream_type": "youtube"},

    {"city": "Queenstown", "country": "New Zealand", "lat": -45.0312, "lon": 168.6626, "count": 14,
     "corridors": ["Lake Wakatipu Steamer Wharf", "Skyline Gondola Observation Deck", "The Mall Pedestrian", "Queenstown Bay Beach"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zM", "stream_type": "youtube"},

    {"city": "Suva", "country": "Fiji", "lat": -18.1416, "lon": 178.4419, "count": 12,
     "corridors": ["Victoria Parade Civic Centre", "Suva Harbour Waterfront", "Albert Park Pavilions", "Government Buildings Clock Tower"],
     "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zM", "stream_type": "youtube"}
]


def generate_global_cameras():
    cameras = []
    cam_counter = 1

    for hub in METROPOLITAN_HUBS:
        city = hub["city"]
        country = hub["country"]
        base_lat = hub["lat"]
        base_lon = hub["lon"]
        count = hub["count"]
        corridors = hub["corridors"]
        stream_url = hub.get("stream_url", "")
        stream_type = hub.get("stream_type", "youtube")

        for i in range(count):
            corr = corridors[i % len(corridors)]
            # Spread camera nodes realistic 1.5km to 14km around city center
            radius_offset = (i * 0.008) + random.uniform(-0.003, 0.003)
            lat = round(base_lat + (radius_offset * 0.7 * random.choice([1, -1])), 5)
            lon = round(base_lon + (radius_offset * 1.0 * random.choice([1, -1])), 5)

            cam_id = f"cam-glob-{cam_counter:05d}"
            name = f"{city} - {corr}"
            if i >= len(corridors):
                name += f" [Node {i + 1}]"

            # Image snapshot fallback
            img_url = f"https://images.earthcam.com/cams/{city.lower().replace(' ', '')}/cam{i+1}.jpg"

            is_primary_hub = (i == 0)
            is_priority = is_primary_hub or (city in [
                "New York City", "Los Angeles", "San Francisco", "London", "Paris", "Tokyo",
                "Berlin", "Rome", "Sydney", "Dubai", "Singapore", "Hong Kong", "Seoul",
                "Shanghai", "Beijing", "Mumbai", "Delhi", "Cairo", "Rio de Janeiro", "Toronto"
            ])

            cameras.append({
                "id": cam_id,
                "name": name,
                "city": f"{city}, {country}",
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "image_url": img_url,
                "stream_url": stream_url if stream_url else img_url,
                "stream_type": stream_type,
                "type": "live_cam",
                "direction": random.choice([
                    "Northbound", "Southbound", "Eastbound", "Westbound",
                    "Plaza Overview", "Waterfront Vista", "Transit Corridor", "Intersection High Angle"
                ]),
                "is_hub": is_primary_hub,
                "priority": "high" if is_priority else "standard"
            })
            cam_counter += 1

    return cameras


def main():
    print("Synthesizing comprehensive planetary CCTV network...")
    cams = generate_global_cameras()
    out_path = os.path.join(os.path.dirname(__file__), "..", "src", "web", "data", "global_cameras.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cams, f, indent=2)

    print(f"Generated {len(cams)} worldwide surveillance cameras across {len(METROPOLITAN_HUBS)} hubs.")
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
