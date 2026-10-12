(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d2cf68c1118c4581.js","sha256":"d2cf68c1118c458103011c9a8a9c3148329b1e51bb3e98b8fb54c902690b68f7","count":2150,"publishedAt":"2026-10-12T11:02:16Z","state":"calendar-state.json","stateSha256":"2cee54f2a8662dec314c3c94a217d54f54149f7174e06fc45a1aa3eba675de96","sourceState":"calendar-source-state.json","sourceStateSha256":"94219b849d94f265567a69ecf85c85978c3d4dfe9bff74ac74d6670d59fbd875"});
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
