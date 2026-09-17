(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e7356180958ba1a4.js","sha256":"e7356180958ba1a406d5fe8309561e5393e76ac74f83ca4040080a93b9b3707f","count":2458,"publishedAt":"2026-09-17T17:08:41Z","state":"calendar-state.json","stateSha256":"2038ac0b2e31da01b7f8e89fd85853f53b000386159236de313e14114812ad8e"});
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
