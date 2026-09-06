(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7b43446f4786dd5e.js","sha256":"7b43446f4786dd5ed699496666985d46dd0adc029b8e5bfd2068996bb0814d97","count":2495,"publishedAt":"2026-09-06T08:20:46Z","state":"calendar-state.json","stateSha256":"fd226b0c24c9dac7315d7eec413696b5a26436cbe7573a39bf0b32166c8cd402"});
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
