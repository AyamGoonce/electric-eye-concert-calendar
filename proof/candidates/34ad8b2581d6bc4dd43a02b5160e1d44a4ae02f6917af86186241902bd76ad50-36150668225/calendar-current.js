(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.34ad8b2581d6bc4d.js","sha256":"34ad8b2581d6bc4dd43a02b5160e1d44a4ae02f6917af86186241902bd76ad50","count":2124,"publishedAt":"2026-09-25T14:59:20Z","state":"calendar-state.json","stateSha256":"0ab376fcddbb38b6d6d988febd27244cc3ded057c522b8810dc43256ca8131be","sourceState":"calendar-source-state.json","sourceStateSha256":"5583c786be2064a13c8c0db77932a75d2887f80e43e1576e3d4c2d038bcb2312"});
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
