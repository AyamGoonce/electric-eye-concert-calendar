(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c465f664c3096977.js","sha256":"c465f664c309697735fab9dcee1a16e27441c0cb57014fe10f2ec32ab8964e8c","count":2034,"publishedAt":"2026-11-06T13:44:39Z","state":"calendar-state.json","stateSha256":"507a31aa37dd5cc88db405a150048913437bdadbadb4dad9e9d9501ea76b059f","sourceState":"calendar-source-state.json","sourceStateSha256":"66536ea616c5a5d56c4431579f9ab041a7ef323dbaad2f98947ef07486c9832f"});
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
