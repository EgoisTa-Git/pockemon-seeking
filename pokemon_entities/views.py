import folium

from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from .models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    pokemon_entities = PokemonEntity.objects.filter(
        appeared_at__lt=timezone.localtime(),
        disappeared_at__gt=timezone.localtime(),
    )
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entity in pokemon_entities:
        if entity.pokemon.image.url:
            add_pokemon(
                folium_map,
                entity.lat,
                entity.lon,
                request.build_absolute_uri(entity.pokemon.image.url),
            )
        else:
            add_pokemon(folium_map, entity.lat, entity.lon)
    pokemons_on_page = []
    pokemons = Pokemon.objects.all()
    for pokemon in pokemons:
        if pokemon.image.url:
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': request.build_absolute_uri(pokemon.image.url),
                'title_ru': pokemon.title,
            })
        else:
            pokemons_on_page.append({
                'pokemon_id': pokemon.id,
                'img_url': DEFAULT_IMAGE_URL,
                'title_ru': pokemon.title,
            })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
        pokemons_entities = pokemon.entities.filter(
            appeared_at__lt=timezone.localtime(),
            disappeared_at__gt=timezone.localtime(),
        )
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemons_entities:
        if pokemon.image.url:
            add_pokemon(
                folium_map, pokemon_entity.lat,
                pokemon_entity.lon,
                request.build_absolute_uri(pokemon.image.url),
            )
        else:
            add_pokemon(folium_map, pokemon_entity.lat, pokemon_entity.lon)
    if pokemon.previous_evolution:
        previous_evolution = {
            'pokemon_id': pokemon.previous_evolution.id,
            'title_ru': pokemon.previous_evolution.title,
            'img_url': pokemon.previous_evolution.image.url,
        }
    else:
        previous_evolution = None
    next_pokemon = pokemon.evolutions.all().first()
    if next_pokemon:
        next_evolution = {
            'pokemon_id': next_pokemon.id,
            'title_ru': next_pokemon.title,
            'img_url': next_pokemon.image.url,
        }
    else:
        next_evolution = None
    if pokemon.image.url:
        img_url = pokemon.image.url
    else:
        img_url = DEFAULT_IMAGE_URL
    pokemon_attributes = {
        'title_ru': pokemon.title,
        'img_url': img_url,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution,
    }
    context = {
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_attributes,
    }
    return render(request, 'pokemon.html', context=context)
