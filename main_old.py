#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from datetime import datetime
import json

from app.utils import get_env
from flask import Flask, jsonify, request, render_template, url_for, send_from_directory, escape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

import pyrez
from pyrez.api import *
from pyrez.exceptions import PlayerNotFound, MatchException
from pyrez.enumerations import Champions, Tier
from langs import *

DEBUG = get_env("DEBUG")
DATABASE_URL = get_env("DATABASE_URL")

app = Flask(__name__, static_folder="static", template_folder="templates", static_url_path='') #https://stackoverflow.com/questions/4239825/static-files-in-flask-robot-txt-sitemap-xml-mod-wsgi
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Session(db.Model):
    __tablename__ = "session"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sessionId = db.Column(db.String(50), unique=True, nullable=False)
    def __init__(self, sessionId):
        self.sessionId = sessionId
        self.save()
    def __repr__(self):
        return "<Session {0.sessionId}>".format(self)
    def save(self):
        try:
            print("SessionId store - ", self)
            for sess in Session.query.all():
                sess.delete()
            db.session.add(self)
            db.session.commit()
        except (IntegrityError, OperationalError, InternalError, ProgrammingError):
            print("SessionId not stored - Database rolledback", self)
            db.session.rollback()
    def update(self, name):
        print("SessionId updated - ", self)
        self.name = name
        db.session.commit()
    def delete(self):
        print("SessionId deleted - ", self)
        db.session.delete(self)
        db.session.commit()
    def json(self):
        return { "session_id": self.sessionId }
class Player(db.Model):
    __tablename__ = "players"
    
    id = db.Column("player_id", db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=False)
    name = db.Column("player_name", db.String(120), nullable=False)
    platform = db.Column("player_platform", db.String(4), nullable=False)

    def __init__(self, id, name, platform):
        self.id = id
        self.name = name
        self.platform = platform
        self.save()
    def __repr__(self):
        return "<Player {0.name} (Id: {0.id} - Platform: {0.platform})>".format(self)
    def save(self):
        try:
            print("Player stored - ", self)
            db.session.add(self)
            db.session.commit()
        except (IntegrityError, OperationalError, InternalError, ProgrammingError):
            print("Player not stored - Database rolledback", self)
            db.session.rollback()
            _player = Player.query.filter_by(id=self.id).first()
            _player.delete()
            self.save()
    def update(self, name):
        print("Player updated - ", self)
        self.name = name
        db.session.commit()
    def delete(self):
        print("Player deleted - ", self)
        db.session.delete(self)
        db.session.commit()
    def json(self):
        return { "player_id": self.id, "player_name": self.name, "player_platform": self.platform }
class BaseEnumeration(Enum):
    def __str__(self):
        return str(self.value).lower()
    def __hash__(self):
        return hash(str(self.value).lower())
class LanguagesSupported(BaseEnumeration):
    English = "en"
    Portuguese = "pt"
    Spanish = "es"
    Polish = "pl"
class PlatformsSupported(BaseEnumeration):
    PC = "pc"
    PTS = "pts"
    Xbox = "10"
    PS4 = "9"
    Switch = "22"
class Outdated(Exception):
    pass
def sessionCreated(session):#print("SESSION: {0}".format(session))
    _session = Session(sessionId=session.sessionId)
    print("New sessionId: {}".format(_session))
try:
    lastSession = Session.query.first()
except (OperationalError, ProgrammingError):
    lastSession = None
print("Last sessionId: {}".format(lastSession))
paladinsAPI = PaladinsAPI(devId=get_env('PYREZ_DEV_ID'), authKey=get_env('PYREZ_AUTH_ID'), sessionId=lastSession.sessionId if lastSession else None)
paladinsAPI.onSessionCreated += sessionCreated
@app.errorhandler(404)
def not_found_error(error=None):
    return INTERNAL_ERROR_404_STRINGS[getLanguage(request)], 200 #return render_template("404.html"), 404 #return INTERNAL_ERROR_404_STRINGS[language], 404
@app.errorhandler(500)
def internal_error(error=None):
    return INTERNAL_ERROR_500_STRINGS[getLanguage(request)], 200 #return render_template("500.html"), 500 #return INTERNAL_ERROR_500_STRINGS[language], 500

#@app.route("/robots.txt", methods=["GET"])
#@app.route("/sitemap.xml", methods=["GET"])
#def staticFromRoot():
#    return send_from_directory(app.static_folder, request.path[1:])
"""
@app.route("/robots.txt")#https://github.com/blampe/template.flask #https://support.google.com/webmasters/answer/93710
def robotsTxt():
    Disallow = lambda string: "Disallow: {}".format(string)
    return Response("User-agent: *\n{}\n".format("\n".join([Disallow("/bin/*"), Disallow("/thank-you"),])))
@app.route("/sitemap.xml", methods=["GET"])
    def sitemap():
      response = make_response(open("sitemap.xml").read())
      response.headers["Content-type"] = "text/plain"
      return response
"""
@app.route('/', methods=["GET"])
@app.route("/api", methods=["GET"])
@app.route("/index", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():#ip = request.remote_addr
    lang = getLanguage(request)
    return render_template("index-{}.html".format(lang), lang=lang) #redirect(url_for("index"))
def formatDecimal(data, form = ",d"):
    return format(data, form) if data else 0
#def encodeData(data):#https://www.urlencoder.io/python/
#    from urllib.parse import quote as URLEncoder #quote_plus
#    return URLEncoder(data)

def getUrl(endpoint, params=None, _external=True):
    _url = url_for(endpoint, _external=_external)
    for param in params:
        _url = _url.replace(param, '')
    return _url
def getAcceptedLanguages(requestArgs):
    return str(request.accept_languages).split('-')[0] if request.accept_languages else LanguagesSupported.English.value
def getLanguage(requestArgs):
    aux = str(requestArgs.args.get("language", default=getAcceptedLanguages(requestArgs))).lower()
    try:
        return LanguagesSupported(aux).value
    except ValueError:
        return LanguagesSupported.English.value
def getChampName(requestArgs):
    qry = requestArgs.get("query", default=None)
    champName = request.args.get("champion", None) if qry is None else qry[qry.rfind('"')+1:].split(' ') if qry.rfind('"') > 1 else qry.split(' ')
    if isinstance(champName, (type(()), type([]))):
        try:
            champName = champName[1]
        except IndexError:
            champName = None
    #return "bombking" if "bk" or "bomb" in champName else "maldamba" if "mal" in champName else champName.lower().replace(" ", "").replace("'", "") if champName else None
    return champName.lower().replace(" ", "").replace("'", "") if champName else None
def getPlatform(requestArgs):
    #_checkOutdated = str(requestArgs.get("platform", default=None)).lower()
    #if str(_checkOutdated) == "platform" or str(_checkOutdated) == "null" or str(_checkOutdated) == "none":
    #    raise Outdated(_checkOutdated)
    qry = requestArgs.get("query", default=None)
    if qry:
        aux = qry[qry.rfind('"')+1:].split(' ') if qry.rfind('"') > 1 else qry.split(' ')
        if isinstance(aux, (type(()), type([]))) and len(aux) > 1:
            aux = aux[len(aux) - 1]
        else:
            aux = str(requestArgs.get("platform", default=None)).lower()
    else:
        aux = str(requestArgs.get("platform", default=None)).lower()
    return PlatformsSupported.Xbox if aux.startswith("xb") else PlatformsSupported.Switch if aux.startswith("switch") else PlatformsSupported.PS4 if aux.startswith("ps") else PlatformsSupported.PTS if aux.startswith("pts") else PlatformsSupported.PC
def getPlayerName(requestArgs):
    qry = requestArgs.get("query", default=None)
    if qry:
        playerName = qry[1:qry.rfind('"')] if qry.rfind('"') > 1 else qry.split(' ')[0]
    else:
        playerName = requestArgs.get("player", default=None)#str(requestArgs.get("query", default=str(requestArgs.get("player", default=None)).lower()).split(' ')[0]).lower()
    return None if not playerName or playerName == "none" or playerName == "null" or playerName == "$(1)" or playerName == "query=$(querystring)" or playerName == "[invalid%20variable]" else escape(playerName.lower())
def getPlayerId(playerName, platform = PlatformsSupported.PC):
    if not playerName or playerName == "none" or playerName == "null" or playerName == "$(1)" or playerName == "query=$(querystring)" or playerName == "[invalid%20variable]":
        return 0
    if str(playerName).isnumeric():
        return playerName if len(str(playerName)) > 5 or len(str(playerName)) < 12 else 0
    if platform == PlatformsSupported.PC:
        playerName = playerName.strip()#.strip(',.-')
    _player = Player.query.filter_by(name=playerName, platform=str(platform)).first()
    print("Player readed - Database", _player)
    if _player is None:
        temp = paladinsAPI.getPlayerId(playerName, platform) if str(platform).isnumeric() else paladinsAPI.getPlayerId(playerName)
        if not temp:
            return -1
        _player = Player(name=playerName, id=temp[0].playerId, platform=str(platform))
    return _player.id if _player else -1
def getLastSeen(lastSeen, language = LanguagesSupported.English):
    now = datetime.utcnow()
    delta = now - lastSeen
    print("Now: {} | Last Seen: {} | Delta: {} | ???: {}".format(now, lastSeen, delta, datetime.now() - lastSeen))
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = "{d}d" if days else "{h}h, {m}m" if hours else "{m}m, {s}s"
    return fmt.format(d=days, h=hours, m=minutes, s=seconds)
@app.route("/api/decks", methods=["GET"])
@app.route("/api/deck", methods=["GET"])
def getDecks():
    try:
        language = getLanguage(request)
        languageCode = 10 if language == "pt" else 12 if language == "pl" else 7 if language == "es" else 1
        championName, playerName, platform = getChampName(request.args), getPlayerName(request.args), getPlatform(request.args)
        
        if championName is None:
            return "ERROR: ChampName not specified!"
        playerId = getPlayerId(playerName, platform)
        if playerId == 0:
            return PLAYER_NULL_STRINGS[language]
        if playerId == -1:
            return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
        playerLoadouts = paladinsAPI.getPlayerLoadouts(playerId, languageCode)
        if len(playerLoadouts) <= 1: #playerLoadouts is None:
            return "{0} doesn't have any {1} custom loadouts!".format(playerName, championName.capitalize())
        cds = ""
        #lambda n: []
        #nums = [str(n) for n in range(20)]
        #print "".join(nums)
        loadouts = [playerLoadout for playerLoadout in playerLoadouts if playerLoadout.godName.lower().replace(" ", "").replace("'", "") == championName.lower()]
        for loadout in loadouts:
            cardStr = "{}{}: {}".format (" " if len(cds) == 0 else ", ", loadout.deckName, ["{0} {1}".format(card.itemName, card.points) for card in loadout.cards]).replace("'", "")
            if len(cds + cardStr) <= 400:
                cds += cardStr
        return cds if cds != "" else "ERROR: {0} doesn't have any {1} custom loadouts! Maybe you misspelled the champName.".format(playerName, championName)
    #except NoResult as exc:
    #    print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
    #    return "Maybe “{}” profile isn't public.".format(playerName)
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return INTERNAL_ERROR_500_STRINGS[language]
@app.route("/api/version", methods=["GET"])
def getGameVersion():
    try:
        language, platform = getLanguage(request), getPlatform(request.args)

        hiRezServerStatus = paladinsAPI.getServerStatus()
        hiRezServerStatus = hiRezServerStatus[1] if platform == PlatformsSupported.Xbox or platform == PlatformsSupported.Switch else hiRezServerStatus[2] if platform == PlatformsSupported.PS4 else hiRezServerStatus[3] if platform == PlatformsSupported.PTS else hiRezServerStatus[0]
        patchInfo = paladinsAPI.getPatchInfo()
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return UNABLE_TO_CONNECT_STRINGS[language]
    return GAME_VERSION_STRINGS[language].format("Paladins", "Xbox One" if platform == PlatformsSupported.Xbox else "PS4" if platform == PlatformsSupported.PS4 else "Nintendo Switch" if platform == PlatformsSupported.Switch else "PTS" if platform == PlatformsSupported.PTS else "PC",
                        PALADINS_UP_STRINGS[language].format(PALADINS_LIMITED_ACCESS_STRINGS[language] if hiRezServerStatus.limitedAccess else "") if hiRezServerStatus.status else PALADINS_DOWN_STRINGS[language],
                        patchInfo.gameVersion, hiRezServerStatus.version)
@app.route("/api/stalk", methods=["GET"])
def getStalk():
    try:
        language, playerName, platform = getLanguage(request), getPlayerName(request.args), getPlatform(request.args)

        playerId = getPlayerId(playerName, platform)
        if playerId == 0:
            return PLAYER_NULL_STRINGS[language]
        if playerId == -1:
            return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
        getPlayerRequest = paladinsAPI.getPlayer(playerId)
        playerStalkRequest = paladinsAPI.getPlayerStatus(playerId)
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except PlayerNotFound as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return INTERNAL_ERROR_500_STRINGS[language]
    return PLAYER_STALK_STRINGS[language].format(PLAYER_LEVEL_STRINGS[language].format(getPlayerRequest.playerName, getPlayerRequest.accountLevel),
                        playerStalkRequest.statusString.replace("God", "Champion").replace("_", " ") if playerStalkRequest.status != 3 else CURRENTLY_MATCH_STRINGS[language].format(QUEUE_IDS_STRINGS[language][playerStalkRequest.queueId], playerStalkRequest.matchId),
                        getPlayerRequest.createdDatetime.strftime(HOUR_FORMAT_STRINGS[language]), getLastSeen(getPlayerRequest.lastLoginDatetime, language), formatDecimal(getPlayerRequest.hoursPlayed), getPlayerRequest.platform, PLAYER_REGION_STRINGS[language][str(getPlayerRequest.playerRegion).replace(' ', "_").upper()])
@app.route("/api/lastmatch", methods=["GET"])
def getLastMatch():
    try:
        language, playerName, platform = getLanguage(request), getPlayerName(request.args), getPlatform(request.args)

        playerId = getPlayerId(playerName, platform)
        if playerId == 0:
            return PLAYER_NULL_STRINGS[language]
        if playerId == -1:
            return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
        lastMatchRequest = paladinsAPI.getMatchHistory(playerId)[0]
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except MatchException as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return INTERNAL_ERROR_500_STRINGS[language]
    kda = ((lastMatchRequest.assists / 2) + lastMatchRequest.kills) / lastMatchRequest.deaths if lastMatchRequest.deaths > 1 else 1
    kda = int(kda) if kda % 2 == 0 else round(kda, 2)
    return LAST_MATCH_STRINGS[language].format(lastMatchRequest.mapName, lastMatchRequest.matchId, lastMatchRequest.godId.getName() if isinstance(lastMatchRequest.godId, Champions) else lastMatchRequest.godName,
                        lastMatchRequest.kills, lastMatchRequest.deaths, lastMatchRequest.assists, kda, lastMatchRequest.killingSpree,
                        formatDecimal(lastMatchRequest.damage), formatDecimal(lastMatchRequest.credits), lastMatchRequest.matchMinutes,
                        PLAYER_REGION_STRINGS[language][str(lastMatchRequest.matchRegion).replace(' ', "_").upper()], MATCH_STRINGS[language][str(lastMatchRequest.winStatus).upper()], "{0}/{1}".format(lastMatchRequest.team1Score,
                        lastMatchRequest.team2Score) if lastMatchRequest.taskForce == 1 else "{0}/{1}".format(lastMatchRequest.team2Score, lastMatchRequest.team1Score))
@app.route("/api/currentmatch", methods=["GET"])
def getCurrentMatch():
    try:
        language, playerName, platform = getLanguage(request), getPlayerName(request.args), getPlatform(request.args)

        playerId = getPlayerId(playerName, platform)
        if playerId == 0 or playerId == -1:
            return PLAYER_NULL_STRINGS[language] if playerId == 0 else PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
        playerStatusRequest = paladinsAPI.getPlayerStatus(playerId)
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return INTERNAL_ERROR_500_STRINGS[language]
    if playerStatusRequest.status != 3:
        return PLAYER_NOT_MATCH_STRINGS[language][playerStatusRequest.status].format(playerName)
    if not playerStatusRequest.queueId.isLiveMatch():#not (playerStatusRequest.queueId.isLiveMatch() or playerStatusRequest.queueId.isPraticeMatch()):
        return QUEUE_ID_NOT_SUPPORTED_STRINGS[language].format(QUEUE_IDS_STRINGS[language][playerStatusRequest.queueId], playerName)
    team1, team2 = [], []
    try:
        players = paladinsAPI.getMatch(playerStatusRequest.matchId, True)
    except LiveMatchException as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return QUEUE_ID_NOT_SUPPORTED_STRINGS[language].format(QUEUE_IDS_STRINGS[language][playerStatusRequest.queueId], playerName)
    if players:
        for player in players:
            if playerStatusRequest.queueId in [ 428, 486 ]:
                rank = PLAYER_RANK_STRINGS[language][player.tier] if player.tier != 0 else PLAYER_RANK_STRINGS[language][0] if player.tierWins + player.tierLosses == 0 else QUALIFYING_STRINGS[language]
            else:
                if player.playerId != "0": #int(player.playerId) != 0:
                    if player.accountLevel >= 15:
                        getPlayer = paladinsAPI.getPlayer(player.playerId)
                        rank = PLAYER_RANK_STRINGS[language][getPlayer.rankedKeyboard.currentRank if getPlayer.rankedKeyboard.hasPlayedRanked() else getPlayer.rankedController.currentRank]
                    else:
                        rank = PLAYER_RANK_STRINGS[language][0]
                else:
                    rank = "???"
            if player.taskForce == 1:
                team1.append(CURRENT_MATCH_PLAYER_STRINGS[language].format(player.playerName if player.playerName else "???", player.godName, rank))
            else:
                team2.append(CURRENT_MATCH_PLAYER_STRINGS[language].format(player.playerName if player.playerName else "???", player.godName, rank))
        return CURRENT_MATCH_STRINGS[language].format(players[0].getMapName(True), QUEUE_IDS_STRINGS[language][playerStatusRequest.queueId], ",".join(team1), ",".join(team2))
    return "An unexpected error has occurred!"
@app.route("/api/rank", methods=["GET"])
def getRank():
    try:
        language, playerName, platform = getLanguage(request), getPlayerName(request.args), getPlatform(request.args)

        playerId = getPlayerId(playerName, platform)
        if playerId == 0:
            return PLAYER_NULL_STRINGS[language]
        if playerId == -1:
            return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
        getPlayerRequest = paladinsAPI.getPlayer(playerId)
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except PlayerNotFound as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return INTERNAL_ERROR_500_STRINGS[language]
    r1, r2 = getPlayerRequest.rankedController, getPlayerRequest.rankedKeyboard
    if not r1.hasPlayed and r2.hasPlayed:
        return PLAYER_GET_RANK_STRINGS[language].format(PLAYER_LEVEL_STRINGS[language].format(getPlayerRequest.playerName, getPlayerRequest.accountLevel),
                                PLAYER_RANK_STRINGS[language][r2.currentRank.value] if r2.currentRank != Tier.Unranked else PLAYER_RANK_STRINGS[language][0] if r2.wins + r2.losses == 0 else QUALIFYING_STRINGS[language],
                                "" if r2.currentRank == Tier.Unranked or r2.currentTrumpPoints <= 0 else " ({0} TP{1})".format(formatDecimal(r2.currentTrumpPoints), ON_LEADERBOARD_STRINGS[language].format(r2.leaderboardIndex) if r2.leaderboardIndex > 0 else ""),
                                "" if r2.currentRank == Tier.Unranked and r2.wins + r2.losses == 0 else WINS_LOSSES_STRINGS[language].format(formatDecimal(r2.wins), formatDecimal(r2.losses)),
                                " (Win rate Global: {0}%{1})".format (getPlayerRequest.winratio, "" if r2.wins + r2.losses == 0 else " & Ranked: {0}%".format(r2.winratio)))
    return PLAYER_GET_RANK_STRINGS[language].format(PLAYER_LEVEL_STRINGS[language].format(getPlayerRequest.playerName, getPlayerRequest.accountLevel),
                                PLAYER_RANK_STRINGS[language][r1.currentRank.value] if r1.currentRank != Tier.Unranked else PLAYER_RANK_STRINGS[language][0] if r1.wins + r1.losses == 0 else QUALIFYING_STRINGS[language],
                                "" if r1.currentRank == Tier.Unranked or r1.currentTrumpPoints <= 0 else " ({0} TP{1})".format(formatDecimal(r1.currentTrumpPoints), ON_LEADERBOARD_STRINGS[language].format(r1.leaderboardIndex) if r1.leaderboardIndex > 0 else ""),
                                "" if r1.currentRank == Tier.Unranked and r1.wins + r1.losses == 0 else WINS_LOSSES_STRINGS[language].format(formatDecimal(r1.wins), formatDecimal(r1.losses)),
                                " (Win rate Global: {0}%{1})".format(getPlayerRequest.winratio, "" if r1.wins + r1.losses == 0 else " & Ranked: {0}%".format(r1.winratio)))
def checkChampName(championName):
    champs = [ "androxus", "atlas", "ash", "barik", "bombking", "buck", "cassie", "dredge", "drogoz", "evie", "fernando", "furia", "grohk", "grover",
    "imani", "inara", "jenos", "khan", "kinessa", "koga", "lex", "lian", "maeve", "makoa", "maldamba", "moji", "pip", "ruckus",
    "seris", "shalin", "skye", "strix", "talus", "terminus", "torvald", "tyra", "viktor", "vivian", "willo", "ying", "zhin" ]
    for champ in champs:
        if champ == championName.lower().replace(" ", "").replace("'", ""):
            return True
    return False
@app.route("/api/kda", methods=["GET"])
@app.route("/api/winrate", methods=["GET"])
def getWinrate():
    try:
        language, championName, playerName, platform = getLanguage(request), getChampName(request.args), getPlayerName(request.args), getPlatform(request.args)
        
        playerId = getPlayerId(playerName, platform)
        if playerId == 0:
            return PLAYER_NULL_STRINGS[language]
        if playerId == -1:
            return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
        getPlayerRequest = paladinsAPI.getPlayer(playerId)
        if getPlayerRequest.accountLevel > 5:
            playerGlobalKDA = paladinsAPI.getChampionRanks(playerId)
        else:
            return PLAYER_LOW_LEVEL_STRINGS[language]
    except Outdated as exc:
        return OUTDATED_CMD_STRINGS[language].format(getUrl('index', params=["index.html", "http://", '/']))
    except PlayerNotFound as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return PLAYER_NOT_FOUND_STRINGS[language].format(playerName)
    except Exception as exc:
        print("{} : {} : {} : {}".format(type(exc), exc.args, exc, str(exc)))
        return INTERNAL_ERROR_500_STRINGS[language]
    if championName:
        if not checkChampName(championName):
            return CHAMP_NOT_PLAYED_STRINGS[language].format(playerName, championName)
        for champ in playerGlobalKDA:
            if champ.godName.lower().replace(" ", "").replace("'", "") == championName:
                return CHAMP_WINRATE_STRINGS[language].format(PLAYER_LEVEL_STRINGS[language].format(champ.godName.replace("'", " "), champ.godLevel), champ.wins, champ.losses,
                        formatDecimal(champ.kills), formatDecimal(champ.deaths), formatDecimal(champ.assists), champ.kda, champ.winratio)
        return CHAMP_NOT_PLAYED_STRINGS[language].format(playerName, championName)
    deaths, kills, assists = 0, 0, 0
    for champ in playerGlobalKDA:
        kills += champ.kills
        deaths += champ.deaths
        assists += champ.assists
    kda = ((assists / 2) + kills) / deaths if deaths > 1 else 1
    return CHAMP_WINRATE_STRINGS[language].format(PLAYER_LEVEL_STRINGS[language].format(getPlayerRequest.playerName, getPlayerRequest.accountLevel), getPlayerRequest.wins, getPlayerRequest.losses,
                        formatDecimal(kills), formatDecimal(deaths), formatDecimal(assists), int(kda) if kda % 2 == 0 else round(kda, 2), getPlayerRequest.winratio)
if __name__ == "__main__":
    if DEBUG:
        #_players = Player.query.filter_by(id="X")
        #for _player in _players:
        #    input(_player)
        #    _player.delete()
        players = Player.query.all()
        print("Entries: {}".format(formatDecimal(len(players))))
        for player in players:
            try:
                p = paladinsAPI.getPlayer(player.id)
                if p.lastLoginDatetime.year < datetime.utcnow().year or p.accountLevel < 15:
                    player.delete()
            except PlayerNotFound:
                player.delete()
            except AttributeError:
                input(p)
            #delete = input("Delete? {}".format(player))
            #if delete.lower() == 'y':
            #    player.delete()
    app.run(debug=DEBUG)
