(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.be294958f57042c0.js","sha256":"be294958f57042c0aba26379443129514c6c1af9143557f1cd0b44ad51297320","count":2193,"publishedAt":"2026-10-10T17:24:34Z","state":"calendar-state.json","stateSha256":"1ebffbbf3cccc977df094d505a147926065b2302c8930dab764d8cb32dd8adc4","sourceState":"calendar-source-state.json","sourceStateSha256":"3cb3a1593ce785fc147a4c633cc05054227cfe56bb53631bb0c48af66fbb6fa7"});
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
