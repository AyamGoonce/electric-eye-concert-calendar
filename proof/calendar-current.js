(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7621832943556de2.js","sha256":"7621832943556de2e111e3137849efd1cf0010b083b2ef4bf4e350f5ab25d6bd","count":2065,"publishedAt":"2026-08-29T09:17:57Z","state":"calendar-state.json","stateSha256":"388e204fcfe07418d7daa3d85f9a6316ef1098ac52adfaaa844c97dee7ed8502"});
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
