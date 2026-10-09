(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ee8666437808bce3.js","sha256":"ee8666437808bce324c322b837d44bcfbae4b5ad0573b5928d7df9e29b3c2565","count":2220,"publishedAt":"2026-10-09T18:26:11Z","state":"calendar-state.json","stateSha256":"fb634ca86afdaebce3d515b928c09a308e0af1b9c1b26adf24bd93a6ee103ad0","sourceState":"calendar-source-state.json","sourceStateSha256":"025b10408eb2d6e35f81f78cada6960b75e97c1c706d7a47487d9ab7edcac824"});
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
