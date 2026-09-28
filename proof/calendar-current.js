(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cf0ec9598a795aa0.js","sha256":"cf0ec9598a795aa0b1b46a5cecacb02f460d0983584b56de137b5e7255aa1507","count":2073,"publishedAt":"2026-09-28T14:05:35Z","state":"calendar-state.json","stateSha256":"b5360a2139cc54ca11f1352af20f226c2b4fc36fba43639e46e634621fd45b0e","sourceState":"calendar-source-state.json","sourceStateSha256":"409950ed3367132acce4051c7cb8af72fdbd03fe5004e4c04054bce7965b6ee1"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
