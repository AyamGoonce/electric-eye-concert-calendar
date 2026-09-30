(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c2a9a25fe62edae8.js","sha256":"c2a9a25fe62edae8153f9cb95f15cdd65b2405915ed4451ca96d6cbc796f8f86","count":2233,"publishedAt":"2026-09-30T23:38:12Z","state":"calendar-state.json","stateSha256":"4696f1891974a2f967277b0ee5506148f5fc4c7d99b354ec4a5374a76ab918b1","sourceState":"calendar-source-state.json","sourceStateSha256":"99fb7a221a1234038e03e9ea1bdb0c5f4222c6495857c8708de9d23cbb2fd7d2"});
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
