(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7df0f268075103b9.js","sha256":"7df0f268075103b9c87ba9111912112c124381605fce24395038b5034514cf68","count":2070,"publishedAt":"2026-10-18T04:43:15Z","state":"calendar-state.json","stateSha256":"ca89f7251859ffb586ad1364a1779e86546cbff8b2aad6b3b13d63b23cd54bcb","sourceState":"calendar-source-state.json","sourceStateSha256":"e05deb462698b9631e053290af70deb1ab9c6a461bbb23d7290bf458f6538404"});
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
