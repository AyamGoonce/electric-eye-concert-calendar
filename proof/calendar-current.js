(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7aad4fe45b2347ac.js","sha256":"7aad4fe45b2347ac4bd9e5e3907d291db494de0505fa99c9decb0195ad36b1e9","count":2106,"publishedAt":"2026-11-24T11:57:49Z","state":"calendar-state.json","stateSha256":"0d9ce04f5b271d070471a11f2288ea493fc25860b4192410fc52e27e24da25ed","sourceState":"calendar-source-state.json","sourceStateSha256":"7a485941f4a6f5f8b80543d5f2bde8b5cc518e8bad77c270a289277292eb5fdf"});
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
