import os
import io
import zipfile
import streamlit as st
import pandas as pd
from scraper import scrape_full_shop, extract_shop_name, analyze_category


st.set_page_config(
    page_title="Etsy Shop Analyzer",
    page_icon="🔍",
    layout="wide",
)

st.title("Etsy Shop Analyzer")

env_key = os.environ.get("SCRAPERAPI_KEY", "")

if env_key:
    scraper_key = env_key
    st.success("Clé ScraperAPI détectée automatiquement.")
else:
    with st.expander("Comment obtenir une clé ScraperAPI (gratuit)", expanded=False):
        st.markdown("""
        1. Allez sur **[scraperapi.com](https://www.scraperapi.com/)** et créez un compte gratuit
        2. Vous obtenez **5 000 requêtes gratuites par mois**
        3. Copiez votre **API Key** depuis le dashboard
        4. Collez-la ci-dessous
        """)

    scraper_key = st.text_input(
        "Clé ScraperAPI",
        type="password",
        help="Créez un compte gratuit sur scraperapi.com pour obtenir votre clé",
    )

mode = st.radio(
    "Mode d'analyse",
    ["Analyser une boutique", "Analyser une catégorie / recherche"],
    horizontal=True,
)

if mode == "Analyser une boutique":
    st.write("Analysez les données d'un vendeur Etsy : ventes, chiffre d'affaires, avis et tags.")

    url = st.text_input(
        "URL ou nom de la boutique Etsy",
        placeholder="https://www.etsy.com/shop/NomDeLaBoutique ou NomDeLaBoutique",
    )

    col_pages1, col_pages2 = st.columns(2)
    with col_pages1:
        max_listing_pages = st.slider("Pages de produits à scanner", 1, 10, 3)
    with col_pages2:
        max_review_pages = st.slider("Pages d'avis à scanner", 1, 20, 5)

    if st.button("Analyser la boutique", type="primary", use_container_width=True):
        if not scraper_key:
            st.error("Veuillez entrer votre clé ScraperAPI.")
        elif not url:
            st.error("Veuillez entrer une URL ou un nom de boutique Etsy.")
        else:
            shop_name = extract_shop_name(url)
            if not shop_name:
                st.error("URL invalide. Utilisez le format : https://www.etsy.com/shop/NomDeLaBoutique ou entrez directement le nom.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(value, text):
                    progress_bar.progress(value)
                    status_text.text(text)

                with st.spinner("Analyse en cours..."):
                    result, error = scrape_full_shop(
                        url,
                        scraper_key,
                        progress_callback=update_progress,
                        max_listing_pages=max_listing_pages,
                        max_review_pages=max_review_pages,
                    )

                progress_bar.empty()
                status_text.empty()

                if error:
                    st.error(error)
                else:
                    st.session_state["result"] = result

elif mode == "Analyser une catégorie / recherche":
    st.write("Recherchez une catégorie ou un mot-clé pour trouver les produits les mieux classés sur Etsy.")

    etsy_categories = {
        "-- Choisir une catégorie --": "",
        "Bijoux & Accessoires": "jewelry accessories",
        "Vêtements & Chaussures": "clothing shoes",
        "Maison & Décoration": "home decor",
        "Mariage & Fêtes": "wedding party",
        "Jouets & Loisirs": "toys games",
        "Art & Collections": "art collectibles",
        "Fournitures créatives": "craft supplies tools",
        "Sacs & Bagagerie": "bags purses",
        "Beauté & Soins": "bath beauty",
        "Électronique & Accessoires": "electronics accessories",
        "Papeterie & Stickers": "paper party supplies stickers",
        "Bougies & Parfums": "candles home fragrance",
        "Impression 3D": "3d printed",
        "Cadeaux personnalisés": "personalized gifts",
        "Vintage": "vintage",
        "Tricot & Crochet": "knitting crochet",
        "Céramique & Poterie": "ceramics pottery",
        "Stickers & Planners": "planner stickers",
        "T-shirts & Vêtements imprimés": "graphic tees shirts",
        "Meubles": "furniture",
        "Produits numériques": "digital downloads",
        "Animaux": "pet supplies accessories",
    }

    selected_cat = st.selectbox("Categorie Etsy", list(etsy_categories.keys()))
    preset_query = etsy_categories[selected_cat]

    if preset_query:
        search_query = st.text_input(
            "Mot-cle (modifiable)",
            value=preset_query,
            placeholder="Ex: planner stickers, bijoux argent, bougies artisanales...",
            key="cat_search_input",
        )
    else:
        search_query = st.text_input(
            "Entrez un mot-cle personnalise",
            placeholder="Ex: planner stickers, bijoux argent, bougies artisanales...",
            key="cat_search_custom",
        )

    cat_col1, cat_col2 = st.columns(2)
    with cat_col1:
        sort_options = {
            "Plus pertinents": "most_relevant",
            "Prix croissant": "price_asc",
            "Prix décroissant": "price_desc",
            "Plus récents": "date_desc",
            "Meilleures ventes": "highest_reviews",
        }
        sort_label = st.selectbox("Trier par", list(sort_options.keys()))
        sort_value = sort_options[sort_label]
    with cat_col2:
        cat_max_pages = st.slider("Nombre de pages à scanner", 1, 10, 3)

    if st.button("Analyser la catégorie", type="primary", use_container_width=True):
        if not scraper_key:
            st.error("Veuillez entrer votre clé ScraperAPI.")
        elif not search_query:
            st.error("Veuillez entrer un mot-clé ou une catégorie.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_cat_progress(value, text):
                progress_bar.progress(value)
                status_text.text(text)

            with st.spinner("Analyse de la catégorie en cours..."):
                cat_result, cat_error = analyze_category(
                    search_query,
                    scraper_key,
                    max_pages=cat_max_pages,
                    sort=sort_value,
                    progress_callback=update_cat_progress,
                )

            progress_bar.empty()
            status_text.empty()

            if cat_error:
                st.error(cat_error)
            else:
                st.session_state["cat_result"] = cat_result

    if "cat_result" in st.session_state:
        cat = st.session_state["cat_result"]

        st.divider()
        st.header(f"Résultats pour : \"{cat['query']}\"")

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.metric("Résultats totaux", f"{cat['total_results']:,}" if cat['total_results'] else "N/A")
        with mc2:
            st.metric("Produits analysés", cat["listings_count"])
        with mc3:
            stats = cat.get("price_stats", {})
            if stats:
                st.metric("Prix moyen", f"{stats['avg']:.2f} $")

        cat_tab1, cat_tab2, cat_tab3, cat_tab4, cat_tab5 = st.tabs([
            "Produits classés",
            "Statistiques de prix",
            "Mots-clés tendance",
            "Boutiques dominantes",
            "Export",
        ])

        with cat_tab1:
            st.subheader("Produits les mieux classés")
            listings = cat.get("listings", [])
            if listings:
                for i, item in enumerate(listings):
                    with st.container():
                        ic1, ic2 = st.columns([1, 5])
                        with ic1:
                            if item.get("image_url"):
                                st.image(item["image_url"], width=120)
                            else:
                                st.write(f"**#{item['position']}**")
                        with ic2:
                            st.write(f"**#{item['position']}** — {item['title']}")
                            info_parts = []
                            if item["price"] > 0:
                                info_parts.append(f"💰 {item['price']:.2f} {item['currency']}")
                            if item.get("rating"):
                                info_parts.append(f"⭐ {item['rating']}")
                            if item.get("shop_name"):
                                info_parts.append(f"🏪 {item['shop_name']}")
                            st.write(" | ".join(info_parts))
                        st.divider()

        with cat_tab2:
            st.subheader("Distribution des prix")
            stats = cat.get("price_stats", {})
            if stats:
                scol1, scol2, scol3, scol4 = st.columns(4)
                with scol1:
                    st.metric("Prix moyen", f"{stats['avg']:.2f} $")
                with scol2:
                    st.metric("Prix médian", f"{stats['median']:.2f} $")
                with scol3:
                    st.metric("Prix min", f"{stats['min']:.2f} $")
                with scol4:
                    st.metric("Prix max", f"{stats['max']:.2f} $")

            price_ranges = cat.get("price_ranges", {})
            if price_ranges:
                ordered_ranges = {}
                for key in ["0-5", "5-10", "10-20", "20-50", "50-100", "100+"]:
                    if key in price_ranges:
                        ordered_ranges[key] = price_ranges[key]
                df_prices = pd.DataFrame({
                    "Tranche de prix ($)": list(ordered_ranges.keys()),
                    "Nombre de produits": list(ordered_ranges.values()),
                })
                st.bar_chart(df_prices.set_index("Tranche de prix ($)"))
                st.dataframe(df_prices, use_container_width=True, hide_index=True)

        with cat_tab3:
            st.subheader("Mots-clés les plus fréquents dans les titres")
            keywords = cat.get("top_keywords", {})
            if keywords:
                df_kw = pd.DataFrame({
                    "Mot-clé": list(keywords.keys()),
                    "Fréquence": list(keywords.values()),
                })
                st.bar_chart(df_kw.set_index("Mot-clé"))
                st.dataframe(df_kw, use_container_width=True, hide_index=True)

        with cat_tab4:
            st.subheader("Boutiques les plus présentes dans les résultats")
            shops = cat.get("top_shops", {})
            if shops:
                df_shops = pd.DataFrame({
                    "Boutique": list(shops.keys()),
                    "Nombre de produits": list(shops.values()),
                })
                st.bar_chart(df_shops.set_index("Boutique"))
                st.dataframe(df_shops, use_container_width=True, hide_index=True)
            else:
                st.info("Aucune boutique identifiée.")

        with cat_tab5:
            listings = cat.get("listings", [])
            if listings:
                df_export = pd.DataFrame([{
                    "Position": l["position"],
                    "Titre": l["title"],
                    "Prix": l["price"],
                    "Devise": l["currency"],
                    "Note": l.get("rating", ""),
                    "Boutique": l.get("shop_name", ""),
                } for l in listings])
                csv = df_export.to_csv(index=False)
                st.download_button(
                    "Télécharger les résultats (CSV)",
                    csv,
                    file_name=f"etsy_category_{cat['query'].replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            import json
            with st.expander("Données brutes (JSON)"):
                export = {
                    "query": cat["query"],
                    "sort": cat["sort"],
                    "total_results": cat["total_results"],
                    "listings_count": cat["listings_count"],
                    "price_stats": cat.get("price_stats", {}),
                    "price_ranges": cat.get("price_ranges", {}),
                    "top_keywords": cat.get("top_keywords", {}),
                    "top_shops": cat.get("top_shops", {}),
                }
                st.json(export)

if mode == "Analyser une boutique" and "result" in st.session_state:
    result = st.session_state["result"]
    shop = result["shop_info"]

    st.divider()

    header_col1, header_col2 = st.columns([1, 5])
    with header_col1:
        if shop.get("icon_url"):
            st.image(shop["icon_url"], width=100)
    with header_col2:
        st.header(f"{shop['shop_name']}")
        if shop.get("title"):
            st.caption(shop["title"])
        if shop.get("shop_location"):
            st.write(f"📍 {shop['shop_location']}")
        if shop.get("member_since"):
            st.write(f"Sur Etsy depuis {shop['member_since']}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ventes totales", f"{shop['total_sales']:,}")
    with col2:
        st.metric("Avis totaux", f"{shop['total_reviews']:,}")
    with col3:
        st.metric("Note moyenne", f"{shop['star_rating']}/5" if shop['star_rating'] else "N/A")
    with col4:
        st.metric("CA estimé", f"{result['estimated_revenue']:,.0f} $")

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Produits scannés", result["listings_count"])
    with col6:
        st.metric("Admirateurs", f"{shop.get('admirers', 0):,}")

    warnings = []
    if shop["total_sales"] == 0:
        warnings.append("Le nombre de ventes n'a pas pu être extrait.")
    if shop["total_reviews"] == 0:
        warnings.append("Le nombre d'avis n'a pas pu être extrait.")
    if result["listings_count"] == 0:
        warnings.append("Aucun produit n'a pu être extrait.")
    if warnings:
        st.warning("Certaines données n'ont pas pu être extraites :\n- " + "\n- ".join(warnings))

    st.caption("Les estimations de ventes mensuelles et de CA sont basées sur une répartition moyenne sur la durée d'activité de la boutique.")

    st.divider()
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Ventes & CA par mois",
        "Avis",
        "Tags",
        "Produits",
        "Derniers avis",
    ])

    with tab1:
        st.subheader("Estimation des ventes mensuelles")
        monthly = result["monthly_sales_estimate"]
        if monthly:
            df_sales = pd.DataFrame({
                "Mois": list(monthly.keys()),
                "Ventes estimées": list(monthly.values()),
            })
            st.bar_chart(df_sales.set_index("Mois"))

            avg_price = 0
            listings = result.get("listings", [])
            prices = [l["price"] for l in listings if l["price"] > 0]
            if prices:
                avg_price = sum(prices) / len(prices)

            if avg_price > 0:
                df_revenue = pd.DataFrame({
                    "Mois": list(monthly.keys()),
                    "CA estimé ($)": [round(v * avg_price, 2) for v in monthly.values()],
                })
                st.subheader("Chiffre d'affaires estimé par mois")
                st.bar_chart(df_revenue.set_index("Mois"))
                st.dataframe(df_revenue, use_container_width=True, hide_index=True)

                st.subheader("Statistiques de prix")
                pcol1, pcol2, pcol3, pcol4 = st.columns(4)
                with pcol1:
                    st.metric("Prix moyen", f"{sum(prices)/len(prices):.2f} $")
                with pcol2:
                    st.metric("Prix médian", f"{sorted(prices)[len(prices)//2]:.2f} $")
                with pcol3:
                    st.metric("Prix min", f"{min(prices):.2f} $")
                with pcol4:
                    st.metric("Prix max", f"{max(prices):.2f} $")
        else:
            st.info("Pas de données de ventes disponibles.")

    with tab2:
        st.subheader("Avis par mois")
        review_months = result["reviews_by_month"]
        if review_months:
            df_reviews = pd.DataFrame({
                "Mois": list(review_months.keys()),
                "Nombre avis": list(review_months.values()),
            })
            st.bar_chart(df_reviews.set_index("Mois"))
            st.dataframe(df_reviews, use_container_width=True, hide_index=True)
        else:
            st.info("Pas de données d'avis avec dates disponibles.")

        st.subheader("Répartition par note")
        review_ratings = result.get("reviews_by_rating", {})
        if review_ratings:
            df_ratings = pd.DataFrame({
                "Note": [f"{'⭐' * int(k)} ({k})" for k in review_ratings.keys()],
                "Nombre": list(review_ratings.values()),
            })
            st.bar_chart(df_ratings.set_index("Note"))
            st.dataframe(df_ratings, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Tags et mots-clés les plus fréquents")
        tags = result["tags"]
        if tags:
            top_tags = dict(list(tags.items())[:25])
            df_tags = pd.DataFrame({
                "Tag": list(top_tags.keys()),
                "Fréquence": list(top_tags.values()),
            })
            st.bar_chart(df_tags.set_index("Tag"))
            st.dataframe(df_tags, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun tag trouvé.")

    with tab4:
        st.subheader("Produits listés")
        listings = result.get("listings", [])
        if listings:
            display_data = []
            for l in listings:
                display_data.append({
                    "Titre": l["title"][:80],
                    "Prix": f"{l['price']:.2f} {l['currency']}",
                    "Tags": ", ".join(l.get("tags", [])[:5]),
                })
            df_listings = pd.DataFrame(display_data)
            st.dataframe(df_listings, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun produit trouvé.")

    with tab5:
        st.subheader("Derniers avis collectés")
        reviews = result.get("reviews", [])
        if reviews:
            for r in reviews[:30]:
                with st.container():
                    rcol1, rcol2 = st.columns([1, 4])
                    with rcol1:
                        st.write(f"**{r.get('date_text', 'N/A')}**")
                        rating = r.get("rating")
                        if rating:
                            st.write("⭐" * int(rating))
                    with rcol2:
                        st.write(r.get("text", "") or "*Pas de commentaire*")
                    st.divider()
        else:
            st.info("Aucun avis trouvé.")

    st.divider()
    st.subheader("Export des données")

    with st.expander("Données brutes (JSON)"):
        import json

        def serialize_dates(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            return str(obj)

        export = {
            "shop_info": result["shop_info"],
            "listings_count": result["listings_count"],
            "reviews_count": result["reviews_count"],
            "estimated_revenue": result["estimated_revenue"],
            "monthly_sales_estimate": result["monthly_sales_estimate"],
            "reviews_by_month": result["reviews_by_month"],
            "reviews_by_rating": result.get("reviews_by_rating", {}),
            "tags": result["tags"],
        }
        st.json(json.loads(json.dumps(export, default=serialize_dates)))

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        listings = result.get("listings", [])
        if listings:
            df_export = pd.DataFrame([{
                "title": l["title"],
                "price": l["price"],
                "currency": l["currency"],
                "tags": "|".join(l.get("tags", [])),
            } for l in listings])
            csv = df_export.to_csv(index=False)
            st.download_button(
                "Télécharger les produits (CSV)",
                csv,
                file_name=f"{shop['shop_name']}_produits.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with col_dl2:
        reviews = result.get("reviews", [])
        if reviews:
            df_reviews_export = pd.DataFrame([{
                "date": r.get("date_text", ""),
                "rating": r.get("rating", ""),
                "text": r.get("text", ""),
            } for r in reviews])
            csv_reviews = df_reviews_export.to_csv(index=False)
            st.download_button(
                "Télécharger les avis (CSV)",
                csv_reviews,
                file_name=f"{shop['shop_name']}_avis.csv",
                mime="text/csv",
                use_container_width=True,
            )


def create_project_zip():
    zip_buffer = io.BytesIO()
    project_files = {
        "app.py": "app.py",
        "scraper.py": "scraper.py",
        "render_requirements.txt": "render_requirements.txt",
        "Dockerfile": "Dockerfile",
        ".dockerignore": ".dockerignore",
        "render.yaml": "render.yaml",
    }
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, filepath in project_files.items():
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    zf.writestr(filename, f.read())
        readme = """# Etsy Shop Analyzer

## Deploiement sur Render

1. Creez un compte sur render.com
2. Creez un "New Web Service"
3. Connectez votre repo GitHub ou uploadez les fichiers
4. Choisissez Docker comme environnement
5. Ajoutez la variable d'environnement SCRAPERAPI_KEY avec votre cle
6. Cliquez sur Deploy

## Deploiement manuel

```bash
pip install -r render_requirements.txt
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
```

## Variables d'environnement

- SCRAPERAPI_KEY : votre cle ScraperAPI (scraperapi.com)
"""
        zf.writestr("README.md", readme)
    zip_buffer.seek(0)
    return zip_buffer


st.divider()
st.subheader("Telecharger le projet")
st.write("Telechargez tous les fichiers necessaires pour deployer sur Render ou un autre serveur.")
zip_data = create_project_zip()
st.download_button(
    "Telecharger le projet complet (ZIP)",
    zip_data,
    file_name="etsy_shop_analyzer.zip",
    mime="application/zip",
    use_container_width=True,
    type="primary",
)
