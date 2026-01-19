#!/usr/bin/env python3
"""
Script para traduzir templates de email para PT e FR
"""

# Traduções PT
translations_pt = {
    # Greeting
    "Hello {{FIRST_NAME}},": "Olá {{FIRST_NAME}},",
    "Thank you for choosing Auto Prudente Rent a Car!": "Obrigado por escolher a Auto Prudente Rent a Car!",
    "We send the vehicle Delivery report and the Terms and Conditions as an attachment.": "Enviamos em anexo o relatório de levantamento da viatura e os Termos e Condições.",
    "If you have any questions or would like to make comments during the rental, do not hesitate to contact us.": "Se tiver dúvidas ou quiser fazer comentários durante o aluguer, não hesite em contactar-nos.",
    
    # Vehicle Details
    "Vehicle & Inspection Details": "Detalhes do Veículo e Inspeção",
    "Customer:": "Cliente:",
    "License Plate:": "Matrícula:",
    "Brand:": "Marca:",
    "Model:": "Modelo:",
    "Type:": "Tipo:",
    "Inspection Type:": "Tipo de Inspeção:",
    "Delivery": "Entrega",
    "Delivery Location:": "Local de Entrega:",
    "Date:": "Data:",
    "Odometer:": "Quilómetros:",
    "Inspector:": "Inspetor:",
    
    # Fuel
    "Fuel Level": "Nível de Combustível",
    "What is the Fuel policy?": "Qual a política de Combustível?",
    "✓ You must return the vehicle with the same fuel level that was delivered to you.": "✓ Tem que devolver a viatura com o mesmo nível de combustível que lhe foi entregue.",
    "✓ You can check the fuel level in the delivery report above.": "✓ Pode consultar o nível de combustível no relatório de entrega enviado em anexo.",
    
    # Damage & Photos
    "Damage Croqui": "Croqui de Danos",
    "Vehicle Photos": "Fotos do Veículo",
    
    # Promotional
    "Where to stay?": "Onde ficar?",
    "Luxury apartments in the heart of Albufeira": "Apartamentos de luxo no Centro de Albufeira",
    "With a privilege location right in front of fishermen's beach in the center of Albufeira, in a six story apartment, enjoy the views and the luxurious view of the beach and the old city. It also stands out by its two panoramic lifts, panoramic pool on the third level and surrounding spaces, private parking and storage. Our apartments are completely furniture and equipped with a lovely and elegant decoration while thinking about your comfort. You can also be delighted in the afternoon by the precious sunset.": "Com localização privilegiada, em frente à praia dos pescadores no centro de Albufeira, um empreendimento com 6 andares, prima de uma privacidade ímpar, e uma impetuosa vista praia e cidade. Destaca-se ainda pelos seus 2 elevadores panorâmicos, piscina panorâmica no 3º piso e espaço envolvente. Parque de estacionamento privativo e elevador interior. Os nossos apartamentos estão completamente mobilados e equipados, com uma decoração elegante e charmosa, a pensar no seu conforto… Pode ainda encantar-se num fim de tarde, com um imperioso por do sol.",
    "More Information": "Mais Informação",
    
    # Traveling by car
    "Traveling by car is an enriching and unforgettable experience": "Viajar de carro é uma experiência enriquecedora e inesquecível",
    "✓ Discover incredible destinations": "✓ Conhecer destinos incríveis",
    "✓ You can discover new landscapes": "✓ Você pode desvendar novas paisagens",
    "✓ Visit places you couldn't go on foot": "✓ Visitar lugares que não conseguiria ir a pé",
    "✓ However, it takes a lot of planning and organization": "✓ No entanto, é preciso muito planeamento e organização",
    
    # Incredible places
    "Incredible places not to be missed!": "Locais incríveis a não perder!",
    "Benagil is a fishing town in the Algarve known for its sea caves and beautiful sandy beaches. Next to Praia de Benagil, the Algar de Benagil cave includes a natural skylight and a small beach.": "Benagil é uma localidade piscatória no Algarve conhecida pelas grutas marinhas e as praias pitorescas. Junto à Praia de Benagil, a gruta do Algar de Benagil inclui uma claraboia natural e uma pequena praia.",
    "It is known for its walled old town, cliffs and Atlantic beaches. Steep wooden steps lead to the sandy cove of Praia do Camilo.": "É conhecida pelas cidade velha amuralhada, pelos penhascos e pelas praias atlânticas. Uns degraus íngremes em madeira levam à enseada arenosa da Praia do Camilo.",
    "Cabo de São Vicente became the patron saint of Lisbon being the crows and the ship, also shown on the Sacred Promontory, which has always been the place used for religious events.": "Cabo de São Vicente tornou-se o padroeiro de Lisboa, tendo como símbolos de Lisboa, os corvos e a nau, também conhecida como Promontório Sagrado, desde sempre que foi local usado para eventos religiosos.",
    
    # Helpful Contacts
    "Helpful Contacts": "Contactos Úteis",
    "OFFICE": "ESCRITÓRIO",
    "TRAVEL ASSISTANCE": "ASSISTÊNCIA EM VIAGEM",
    "EMERGENCY": "EMERGÊNCIA",
    
    # Footer
    "© 2026 Auto Prudente Rent a Car. All rights reserved.": "© 2026 Auto Prudente Rent a Car. Todos os direitos reservados.",
    "You are receiving this email because you have signed a vehicle rental contract with Auto Prudente Rent a Car. As data controller, Auto Prudente Rent a Car Unipessoal, Lda. processes your personal data to send you information and services related to your rental, processing related to the execution of your vehicle rental contract. For more information about how Auto Prudente Rent a Car processes your personal data and your rights under data protection law, please consult our privacy policy.": "Está a receber este e-mail porque efetuou um contrato aluguer de um veículo com a Auto Prudente Rent a Car. Como responsável pelo tratamento de dados, a Auto Prudente Rent a Car Unipessoal, Lda. processa os seus dados pessoais para lhe enviar informações e serviços relacionados com o seu aluguer, processamento esse relativo à execução do seu contrato de aluguer de veículo. Para obter mais informações sobre como a Auto Prudente Rent a Car processa os seus dados pessoais e sobre os seus direitos sob a lei de proteção de dados, por favor consulte a nossa política de privacidade.",
    "Auto Prudente Rent a Car Unipessoal, Lda. - Fiscal Number: PT 503 539 791 – Main Office: Estrada de Santa Eulália, Edifício Onda do Mar Loja E, 8200-269 Albufeira Telefone +351 289 542 160 ; E- mail: info@auto-prudente.com": "Auto Prudente Rent a Car Unipessoal, Lda. - Contribuinte Fiscal n.º PT 503 539 791 - Sede: Estrada de Santa Eulália, Edifício Onda do Mar Loja E, 8200-269 Albufeira Telefone +351 289 542 160 ; E-mail: info@auto-prudente.com",
    "Contact Us": "Contacte-nos",
    "Available during office hours": "Disponível durante o horário de expediente",
}

# Traduções FR
translations_fr = {
    # Greeting
    "Hello {{FIRST_NAME}},": "Bonjour {{FIRST_NAME}},",
    "Thank you for choosing Auto Prudente Rent a Car!": "Merci d'avoir choisi Auto Prudente Rent a Car!",
    "We send the vehicle Delivery report and the Terms and Conditions as an attachment.": "Nous envoyons en pièce jointe le rapport de livraison du véhicule et les Conditions Générales.",
    "If you have any questions or would like to make comments during the rental, do not hesitate to contact us.": "Si vous avez des questions ou souhaitez faire des commentaires pendant la location, n'hésitez pas à nous contacter.",
    
    # Vehicle Details
    "Vehicle & Inspection Details": "Détails du Véhicule et de l'Inspection",
    "Customer:": "Client:",
    "License Plate:": "Plaque d'immatriculation:",
    "Brand:": "Marque:",
    "Model:": "Modèle:",
    "Type:": "Type:",
    "Inspection Type:": "Type d'Inspection:",
    "Delivery": "Livraison",
    "Delivery Location:": "Lieu de Livraison:",
    "Date:": "Date:",
    "Odometer:": "Kilométrage:",
    "Inspector:": "Inspecteur:",
    
    # Fuel
    "Fuel Level": "Niveau de Carburant",
    "What is the Fuel policy?": "Quelle est la politique de carburant?",
    "✓ You must return the vehicle with the same fuel level that was delivered to you.": "✓ Vous devez retourner le véhicule avec le même niveau de carburant qui vous a été livré.",
    "✓ You can check the fuel level in the delivery report above.": "✓ Vous pouvez vérifier le niveau de carburant dans le rapport de livraison ci-dessus.",
    
    # Damage & Photos
    "Damage Croqui": "Croquis des Dommages",
    "Vehicle Photos": "Photos du Véhicule",
    
    # Promotional
    "Where to stay?": "Où séjourner?",
    "Luxury apartments in the heart of Albufeira": "Appartements de luxe au cœur d'Albufeira",
    "With a privilege location right in front of fishermen's beach in the center of Albufeira, in a six story apartment, enjoy the views and the luxurious view of the beach and the old city. It also stands out by its two panoramic lifts, panoramic pool on the third level and surrounding spaces, private parking and storage. Our apartments are completely furniture and equipped with a lovely and elegant decoration while thinking about your comfort. You can also be delighted in the afternoon by the precious sunset.": "Avec un emplacement privilégié juste en face de la plage des pêcheurs au centre d'Albufeira, dans un immeuble de six étages, profitez des vues et de la vue luxueuse sur la plage et la vieille ville. Il se distingue également par ses deux ascenseurs panoramiques, sa piscine panoramique au 3ème niveau et ses espaces environnants, son parking privé et son rangement. Nos appartements sont entièrement meublés et équipés, avec une décoration charmante et élégante en pensant à votre confort. Vous pouvez également être enchanté l'après-midi par le précieux coucher de soleil.",
    "More Information": "Plus d'Informations",
    
    # Traveling by car
    "Traveling by car is an enriching and unforgettable experience": "Voyager en voiture est une expérience enrichissante et inoubliable",
    "✓ Discover incredible destinations": "✓ Découvrir des destinations incroyables",
    "✓ You can discover new landscapes": "✓ Vous pouvez découvrir de nouveaux paysages",
    "✓ Visit places you couldn't go on foot": "✓ Visiter des endroits où vous ne pourriez pas aller à pied",
    "✓ However, it takes a lot of planning and organization": "✓ Cependant, cela demande beaucoup de planification et d'organisation",
    
    # Incredible places
    "Incredible places not to be missed!": "Lieux incroyables à ne pas manquer!",
    "Benagil is a fishing town in the Algarve known for its sea caves and beautiful sandy beaches. Next to Praia de Benagil, the Algar de Benagil cave includes a natural skylight and a small beach.": "Benagil est une ville de pêcheurs en Algarve connue pour ses grottes marines et ses belles plages de sable. À côté de Praia de Benagil, la grotte d'Algar de Benagil comprend un puits de lumière naturel et une petite plage.",
    "It is known for its walled old town, cliffs and Atlantic beaches. Steep wooden steps lead to the sandy cove of Praia do Camilo.": "Elle est connue pour sa vieille ville fortifiée, ses falaises et ses plages atlantiques. Des marches en bois raides mènent à la crique sablonneuse de Praia do Camilo.",
    "Cabo de São Vicente became the patron saint of Lisbon being the crows and the ship, also shown on the Sacred Promontory, which has always been the place used for religious events.": "Cabo de São Vicente est devenu le saint patron de Lisbonne avec les corbeaux et le navire, également représenté sur le Promontoire Sacré, qui a toujours été le lieu utilisé pour les événements religieux.",
    
    # Helpful Contacts
    "Helpful Contacts": "Contacts Utiles",
    "OFFICE": "BUREAU",
    "TRAVEL ASSISTANCE": "ASSISTANCE VOYAGE",
    "EMERGENCY": "URGENCE",
    
    # Footer
    "© 2026 Auto Prudente Rent a Car. All rights reserved.": "© 2026 Auto Prudente Rent a Car. Tous droits réservés.",
    "You are receiving this email because you have signed a vehicle rental contract with Auto Prudente Rent a Car. As data controller, Auto Prudente Rent a Car Unipessoal, Lda. processes your personal data to send you information and services related to your rental, processing related to the execution of your vehicle rental contract. For more information about how Auto Prudente Rent a Car processes your personal data and your rights under data protection law, please consult our privacy policy.": "Vous recevez cet e-mail parce que vous avez signé un contrat de location de véhicule avec Auto Prudente Rent a Car. En tant que responsable du traitement des données, Auto Prudente Rent a Car Unipessoal, Lda. traite vos données personnelles pour vous envoyer des informations et des services liés à votre location, traitement lié à l'exécution de votre contrat de location de véhicule. Pour plus d'informations sur la manière dont Auto Prudente Rent a Car traite vos données personnelles et sur vos droits en vertu de la loi sur la protection des données, veuillez consulter notre politique de confidentialité.",
    "Auto Prudente Rent a Car Unipessoal, Lda. - Fiscal Number: PT 503 539 791 – Main Office: Estrada de Santa Eulália, Edifício Onda do Mar Loja E, 8200-269 Albufeira Telefone +351 289 542 160 ; E- mail: info@auto-prudente.com": "Auto Prudente Rent a Car Unipessoal, Lda. - Numéro Fiscal: PT 503 539 791 – Siège Social: Estrada de Santa Eulália, Edifício Onda do Mar Loja E, 8200-269 Albufeira Téléphone +351 289 542 160 ; E-mail: info@auto-prudente.com",
    "Contact Us": "Contactez-nous",
    "Available during office hours": "Disponible pendant les heures de bureau",
    
    # Additional FR translations
    "<strong>✓</strong> Discover incredible destinations": "<strong>✓</strong> Découvrir des destinations incroyables",
    "<strong>✓</strong> You can discover new landscapes": "<strong>✓</strong> Vous pouvez découvrir de nouveaux paysages",
    "<strong>✓</strong> Visit places you couldn't go on foot": "<strong>✓</strong> Visiter des endroits où vous ne pourriez pas aller à pied",
    "<strong>✓</strong> However, it takes a lot of planning and organization": "<strong>✓</strong> Cependant, cela demande beaucoup de planification et d'organisation",
}

def translate_template(input_file, output_file, translations):
    """Traduz um template HTML usando o dicionário de traduções"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aplicar traduções
    for english, translation in translations.items():
        content = content.replace(english, translation)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Template traduzido: {output_file}")

if __name__ == "__main__":
    # Traduzir para PT
    translate_template(
        'templates/email_preview.html',
        'templates/email_preview_pt.html',
        translations_pt
    )
    
    # Traduzir para FR
    translate_template(
        'templates/email_preview.html',
        'templates/email_preview_fr.html',
        translations_fr
    )
    
    print("\n✅ Todos os templates traduzidos com sucesso!")
