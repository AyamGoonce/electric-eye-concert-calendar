(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.af4df717d2a1a2cd.js","sha256":"af4df717d2a1a2cdbd5eb1e5863290f07f96204a16797f563c9d04174da055da","count":2154,"publishedAt":"2026-10-15T17:09:05Z","state":"calendar-state.json","stateSha256":"d40d6794449ca17c8bfd82a9358b081ae570e209b91b7bcc56cb542804a3312c","sourceState":"calendar-source-state.json","sourceStateSha256":"11797741eb62409ef5e7cfe3bbd89df16c17be7b674ba517d9d9c21b477a1501"});
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
