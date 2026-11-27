(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.01898aec643dee94.js","sha256":"01898aec643dee94006726cf9b521e06933529827e05049e0ebc1c67ea100188","count":2125,"publishedAt":"2026-11-27T15:10:49Z","state":"calendar-state.json","stateSha256":"6b26a950105119422777ba264a689b42960ad511320ba441d326105048b72c1f","sourceState":"calendar-source-state.json","sourceStateSha256":"b891e4d8035925fc04bac004123e8a7338f50bfbe9cfcc521bb54f67bd569ceb"});
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
