(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a81d968d8ca27371.js","sha256":"a81d968d8ca2737113dfae62767db5d7aa5442c16c66fd6b47ffd413eb3e98ce","count":2459,"publishedAt":"2026-09-07T09:15:26Z","state":"calendar-state.json","stateSha256":"d7451bebd177f5e6660fc3c627e984100d1bfc70f32231f47d6286fc108d0843"});
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
