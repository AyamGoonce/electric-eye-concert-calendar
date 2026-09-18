(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ddbe5d35bfccfa81.js","sha256":"ddbe5d35bfccfa810c42977b76fec4b79a57ee3bf55c11cd39567b319fdd57f1","count":2131,"publishedAt":"2026-09-18T23:26:24Z","state":"calendar-state.json","stateSha256":"fc7bd12476fdcebf686bab90fcdff3c0f557047faae1c88af498858700fa356e"});
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
