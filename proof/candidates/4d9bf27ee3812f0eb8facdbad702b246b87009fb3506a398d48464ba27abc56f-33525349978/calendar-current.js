(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4d9bf27ee3812f0e.js","sha256":"4d9bf27ee3812f0eb8facdbad702b246b87009fb3506a398d48464ba27abc56f","count":2265,"publishedAt":"2026-09-01T15:32:41Z","state":"calendar-state.json","stateSha256":"f8c532e69a27f5fabfed3d568488017cfd2f5d25417462ec735bef480925c782"});
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
