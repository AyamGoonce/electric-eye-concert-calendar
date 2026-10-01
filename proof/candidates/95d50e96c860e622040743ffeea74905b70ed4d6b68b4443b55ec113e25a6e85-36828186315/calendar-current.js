(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.95d50e96c860e622.js","sha256":"95d50e96c860e622040743ffeea74905b70ed4d6b68b4443b55ec113e25a6e85","count":2220,"publishedAt":"2026-10-01T07:04:26Z","state":"calendar-state.json","stateSha256":"4514584098a04948e3b46f439b0647c659b43f6028ee279d21d77147166b20ed","sourceState":"calendar-source-state.json","sourceStateSha256":"9b8cb38c65d367412e44f1d5a6f2723134bf2621140533d9025c32762ee3f0bc"});
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
