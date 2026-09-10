(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3db377b46257de71.js","sha256":"3db377b46257de7108da788e41db9697e7be62a18a0cbfc4b601c28ba1a488e1","count":2442,"publishedAt":"2026-09-10T07:01:55Z","state":"calendar-state.json","stateSha256":"89a86940115173902d0643707aa8684dd56432db9908ae51190f949152bf7cd1"});
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
