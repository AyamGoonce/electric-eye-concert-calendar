(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.793c678fe49d42ce.js","sha256":"793c678fe49d42ce21861203ff1888af3c23df9983a5978a87f795e73b164c9e","count":2070,"publishedAt":"2026-10-19T13:30:31Z","state":"calendar-state.json","stateSha256":"666b38fb47414735e47d66aa749d08af41036e49375239e3756d8e4cfcd00b68","sourceState":"calendar-source-state.json","sourceStateSha256":"0487a6d4c775fe1416219445fd8d6d1472de12cd6a16fa223febd01198c5e22b"});
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
