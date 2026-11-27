(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.68e6ec4b300b8261.js","sha256":"68e6ec4b300b826165f64f048a930c3a67f0ab812fdd7881af17adeb2d4a247a","count":2128,"publishedAt":"2026-11-27T15:40:39Z","state":"calendar-state.json","stateSha256":"fd9ac4cfeba2d93ddc5cd5d8985248b82d2001e2eefbf702f98a6c86573d8893","sourceState":"calendar-source-state.json","sourceStateSha256":"7d6559f6505bed2cf3dcb7241c9e931f8086e59df5f70b15e2c300687544e446"});
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
