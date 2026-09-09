(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.00c6bd43c88164cb.js","sha256":"00c6bd43c88164cbf03fd5101c1aa0394169551fec19a922858ae208514de570","count":2454,"publishedAt":"2026-09-09T20:37:40Z","state":"calendar-state.json","stateSha256":"a87138868bfd59b066e7f4dc30ed51e8792efd3febd970f4043eb508ce9f912a"});
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
